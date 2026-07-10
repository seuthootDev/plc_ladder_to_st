from __future__ import annotations

import html
import os
import re
import time
from datetime import datetime
from pathlib import Path

from .models import ProgramIR
from .paths import ENV_FILE, PROJECT_ROOT
from .ladder_patterns.prompt_builder import build_pattern_guide
from .st_parser import parse_st, parse_st_file

DEFAULT_GEMINI_MODEL = "gemini-2.0-flash"

DEFAULT_RETRY_MAX = 0
DEFAULT_RETRY_BASE_DELAY = 10.0
DEFAULT_RETRY_MAX_DELAY = 120.0
DEFAULT_REQUEST_DELAY = 3.0

LADDER_PROMPT = """You convert Mitsubishi PLC Structured Text (ST) into ONE SVG ladder diagram.

Follow these HARD RULES exactly. Do not invent alternate styles.

=== CANVAS ===
- White background (#ffffff).
- Left power rail ONLY at x=16, full rung height, stroke #374151, stroke-width 3.
- Do NOT draw a right power rail.
- Each rung separated by a thin horizontal line (#e5e7eb, stroke-width 1).

=== GRID / SPACING (fixed) ===
- Contact cell: 56 x 26 px.
- Coil cell: 80 x 26 px.
- Timer cell: 100 x 36 px.
- Horizontal gap between series elements: 6 px.
- Vertical gap between parallel OR branches: 42 px (contact center to center).
- Rung label column width: 180 px from left rail.
- First rung starts at y=40; each rung block ~100-120 px tall depending on branch count.

=== TYPOGRAPHY (never change) ===
- Device labels (M202, Y20, T100, X1C ...):
  font-family="Consolas, 'Courier New', monospace"
  font-size="10" font-weight="bold" fill="#111827" text-anchor="middle"
  placed ABOVE the symbol center.
- Rung labels (left column):
  font-family="Consolas, 'Courier New', monospace"
  font-size="10" font-weight="normal" fill="#111827" text-anchor="start"
  format exactly: "R{{n}}  step {{step}}" using ST rung comments.
- Program title (top):
  font-family="Segoe UI, sans-serif" font-size="13" font-weight="bold" fill="#111827"
  format: "{{program_name}}  |  {{project}}"

=== WIRES ===
- All wires: stroke #374151, stroke-width 2, stroke-linecap="round", fill="none".
- Draw junction dots (circle r=2.5 fill #374151) at every T-junction / branch merge.

=== CONTACTS (M, X, SM, etc.) ===
- NO contact: two vertical blue bars (#2563eb, stroke-width 2.5), 14 px apart, height 18 px.
- NC contact: same bars PLUS one diagonal slash (#2563eb, stroke-width 2).
- Horizontal wire enters left, exits right through contact center y.
- Never use Unicode "| |" text as symbols; always draw geometry.

=== COILS / OUTPUTS ===
- Coil: ellipse rx=34 ry=11, fill #fff, stroke #dc2626 stroke-width 2.
- SET coil: prefix label "S" before device name inside/near coil.
- RST coil: prefix label "R" before device name.
- Timer: rounded rect, stroke #d97706, label like "T100" and preset "T#8000ms" below or inside box.

=== LOGIC LAYOUT ===
- AND: elements in series on the same horizontal rail, left to right.
- OR: multiple parallel horizontal rails; connect each branch to left vertical bus;
  merge branches with a vertical bus on the right side of the OR group, then continue to coil.
- Nested OR/AND: use additional parallel rails; never draw diagonal shortcuts.
- One rung = one output coil/timer/set/rst at the far right of that rung (except special multi-output if ST explicitly has them).
- Preserve ST device names exactly (M202, SM412, Y3C, /X1C for NC inputs if present in ST).

=== FORBIDDEN ===
- No CSS class-based theming that changes per rung.
- No varying font families or sizes between rungs.
- No decorative headers, gradients, shadows, or icons.
- No markdown in output.
- No right-side power rail.
- No ASCII-art ladder text.

=== OUTPUT ===
- Output ONLY valid SVG XML: starts with <?xml or <svg, ends with </svg>.
- Use explicit numeric coordinates (no percentage layout).
- Group wires, symbols, labels in <g> if helpful, but keep style consistent.

Program: {program_name}
Project: {project}

{pattern_guide}

ST source:
```
{st_text}
```
"""

_PLACEHOLDER_KEYS = frozenset({"", "your_api_key_here", "your-api-key-here"})


def _valid_api_key(key: str) -> bool:
    return bool(key.strip()) and key.strip().lower() not in _PLACEHOLDER_KEYS


def load_dotenv() -> None:
    try:
        from dotenv import load_dotenv as _load
    except ImportError as exc:
        raise ImportError(
            "AI ladder requires python-dotenv: pip install python-dotenv"
        ) from exc

    for path in (
        ENV_FILE,
        PROJECT_ROOT / ".env.local",
        Path.cwd() / ".env",
        Path.cwd() / ".env.local",
    ):
        if path.exists():
            _load(path, override=False)

    if not any(
        _valid_api_key(os.getenv(name, ""))
        for name in ("GEMINI_API_KEY", "GOOGLE_API_KEY")
    ):
        _load(override=False)


def gemini_api_key() -> str:
    load_dotenv()
    for name in ("GEMINI_API_KEY", "GOOGLE_API_KEY"):
        key = os.getenv(name, "").strip()
        if _valid_api_key(key):
            return key
    raise RuntimeError(
        "GEMINI_API_KEY (or GOOGLE_API_KEY) is not set. In the plc folder run:\n"
        "  copy .env.example .env\n"
        f"Or create {PROJECT_ROOT / '.env.local'} with your API key "
        "(https://aistudio.google.com/apikey)"
    )


def gemini_model() -> str:
    load_dotenv()
    for name in ("GEMINI_MODEL", "GOOGLE_GEMINI_MODEL"):
        value = os.getenv(name, "").strip()
        if value:
            return value
    return DEFAULT_GEMINI_MODEL


def build_prompt(program: ProgramIR, st_text: str) -> str:
    impl_start = st_text.find("(* --- Rung")
    impl = st_text[impl_start:] if impl_start >= 0 else st_text
    if len(impl) > 24000:
        impl = impl[:24000] + "\n(* ... truncated ... *)"
    pattern_guide = build_pattern_guide(program)
    if len(pattern_guide) > 12000:
        pattern_guide = pattern_guide[:12000] + "\n(* ... pattern guide truncated ... *)"
    return LADDER_PROMPT.format(
        program_name=program.name,
        project=program.project or "unknown",
        pattern_guide=pattern_guide,
        st_text=impl,
    )


def extract_svg(raw: str) -> str:
    text = raw.strip()
    fenced = re.search(r"```(?:svg|xml)?\s*([\s\S]*?)```", text, re.IGNORECASE)
    if fenced:
        text = fenced.group(1).strip()
    svg_start = text.find("<svg")
    if svg_start < 0:
        raise ValueError("Gemini response did not contain <svg> markup")
    text = text[svg_start:]
    svg_end = text.lower().rfind("</svg>")
    if svg_end < 0:
        raise ValueError("Gemini response SVG is incomplete (missing </svg>)")
    svg = text[: svg_end + len("</svg>")]
    if not svg.lstrip().startswith("<?xml"):
        svg = '<?xml version="1.0" encoding="UTF-8"?>\n' + svg
    return svg


def _gemini_retry_config() -> tuple[int, float, float, float]:
    load_dotenv()
    max_retries = int(os.getenv("GEMINI_RETRY_MAX", str(DEFAULT_RETRY_MAX)))
    base_delay = float(os.getenv("GEMINI_RETRY_BASE_DELAY", str(DEFAULT_RETRY_BASE_DELAY)))
    max_delay = float(os.getenv("GEMINI_RETRY_MAX_DELAY", str(DEFAULT_RETRY_MAX_DELAY)))
    request_delay = float(os.getenv("GEMINI_REQUEST_DELAY", str(DEFAULT_REQUEST_DELAY)))
    return max(0, max_retries), max(0.0, base_delay), max(0.0, max_delay), max(0.0, request_delay)


def _backoff_delay(attempt: int, base_delay: float, max_delay: float) -> float:
    return min(base_delay * (2 ** min(attempt, 6)), max_delay)


_NETWORK_ERROR_NAMES = frozenset({
    "RemoteProtocolError",
    "ConnectError",
    "ReadError",
    "WriteError",
    "NetworkError",
    "TimeoutException",
    "PoolTimeout",
    "ProtocolError",
    "ReadTimeout",
    "ConnectTimeout",
})

_RETRY_MESSAGE_TOKENS = (
    "empty response",
    "did not contain <svg>",
    "svg is incomplete",
    "503",
    "429",
    "502",
    "504",
    "unavailable",
    "high demand",
    "peer closed",
    "incomplete chunked",
    "connection reset",
    "broken pipe",
    "timed out",
    "timeout",
    "temporarily unavailable",
    "server disconnected",
    "connection aborted",
)


def _is_retryable_gemini_error(exc: Exception) -> bool:
    try:
        from google.genai import errors
    except ImportError:
        return False
    if isinstance(exc, errors.ServerError):
        return getattr(exc, "code", 0) in (429, 500, 502, 503, 504)
    if isinstance(exc, errors.ClientError):
        return getattr(exc, "code", 0) == 429
    return False


def _is_retryable_ladder_error(exc: Exception) -> bool:
    if _is_retryable_gemini_error(exc):
        return True

    if isinstance(exc, (ConnectionError, TimeoutError, OSError)):
        return True

    exc_name = type(exc).__name__
    if exc_name in _NETWORK_ERROR_NAMES:
        return True

    module = type(exc).__module__ or ""
    if any(part in module for part in ("httpx", "httpcore", "urllib3", "requests")):
        return True

    message = str(exc).lower()
    return any(token in message for token in _RETRY_MESSAGE_TOKENS)


def _error_label(exc: Exception) -> str:
    code = getattr(exc, "code", None)
    if code is not None:
        return str(code)
    return type(exc).__name__


def call_gemini(prompt: str) -> str:
    try:
        from google import genai
    except ImportError as exc:
        raise ImportError(
            "AI ladder requires google-genai: pip install google-genai"
        ) from exc

    client = genai.Client(api_key=gemini_api_key())
    model = gemini_model()
    max_retries, base_delay, max_delay, _ = _gemini_retry_config()
    unlimited = max_retries == 0

    attempt = 0
    while True:
        try:
            response = client.models.generate_content(
                model=model,
                contents=prompt,
            )
            text = getattr(response, "text", None)
            if not text:
                raise RuntimeError("Empty response from Gemini API")
            return text
        except Exception as exc:
            if not _is_retryable_ladder_error(exc):
                raise
            if not unlimited and attempt >= max_retries:
                raise
            delay = _backoff_delay(attempt, base_delay, max_delay)
            attempt += 1
            label = _error_label(exc)
            if unlimited:
                print(f"  Gemini request {label}, retry #{attempt} in {delay:.0f}s...")
            else:
                print(
                    f"  Gemini request {label} (attempt {attempt}/{max_retries}), "
                    f"retry in {delay:.0f}s..."
                )
            time.sleep(delay)


def render_ai_html(program: ProgramIR, svg: str, *, model: str) -> str:
    safe_name = html.escape(program.name)
    safe_project = html.escape(program.project or "")
    rung_count = len(program.rungs)
    unsupported = html.escape("\n".join(program.unsupported) or "none")
    generated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    safe_model = html.escape(model)
    return f"""<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{safe_name} Ladder View (AI)</title>
  <style>
    body {{ margin: 0; font-family: "Segoe UI", sans-serif; background: #f8fafc; color: #111827; }}
    header {{ padding: 16px 20px; background: #1e3a5f; color: #fff; }}
    header h1 {{ margin: 0 0 4px; font-size: 18px; }}
    header p {{ margin: 0; font-size: 13px; color: #cbd5e1; }}
    .badge {{ display: inline-block; background: #7c3aed; color: #fff; font-size: 11px; padding: 2px 8px; border-radius: 999px; margin-left: 8px; vertical-align: middle; }}
    .wrap {{ padding: 16px; overflow: auto; }}
    .panel {{ background: #fff; border: 1px solid #e5e7eb; border-radius: 8px; padding: 12px; margin-bottom: 12px; }}
    svg {{ display: block; width: auto; height: auto; max-width: none; }}
  </style>
</head>
<body>
  <header>
    <h1>{safe_name}<span class="badge">AI track</span></h1>
    <p>{safe_project} · rung {rung_count} · Gemini {safe_model} · {generated_at}</p>
  </header>
  <div class="wrap">
    <div class="panel">{svg}</div>
    <div class="panel">
      <strong>Parse warnings</strong>
      <pre style="white-space: pre-wrap; font-size: 12px;">{unsupported}</pre>
    </div>
  </div>
</body>
</html>
"""


def st_text_to_ai_ladder(st_text: str, *, name: str = "") -> tuple[str, str, ProgramIR]:
    program = parse_st(st_text, name=name)
    prompt = build_prompt(program, st_text)
    raw = call_gemini(prompt)
    svg = extract_svg(raw)
    html_doc = render_ai_html(program, svg, model=gemini_model())
    return svg, html_doc, program


def st_file_to_ai_ladder(st_path: str | Path) -> tuple[str, str, ProgramIR]:
    path = Path(st_path)
    st_text = path.read_text(encoding="utf-8")
    program = parse_st_file(path)
    prompt = build_prompt(program, st_text)
    raw = call_gemini(prompt)
    svg = extract_svg(raw)
    html_doc = render_ai_html(program, svg, model=gemini_model())
    return svg, html_doc, program


def render_all_ai(
    st_dir: str | Path,
    output_dir: str | Path,
    *,
    html: bool = True,
    skip_existing: bool = False,
    wait_until_success: bool = True,
    continue_on_error: bool = False,
) -> tuple[list[Path], list[str]]:
    st_dir = Path(st_dir)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    failures: list[str] = []
    _, base_delay, max_delay, request_delay = _gemini_retry_config()
    st_files = sorted(st_dir.glob("P*.st"))
    total = len(st_files)

    for index, st_path in enumerate(st_files, start=1):
        svg_path = output_dir / f"{st_path.stem}.svg"
        html_path = output_dir / f"{st_path.stem}.html"
        if skip_existing and svg_path.exists():
            print(f"AI ladder [{index}/{total}]: {st_path.name} (skip, already exists)")
            written.append(svg_path)
            if html and html_path.exists():
                written.append(html_path)
            continue

        print(f"AI ladder [{index}/{total}]: {st_path.name} ...")
        attempt = 0
        svg: str | None = None
        html_doc: str | None = None
        while True:
            try:
                svg, html_doc, _ = st_file_to_ai_ladder(st_path)
                break
            except Exception as exc:
                if wait_until_success and _is_retryable_ladder_error(exc):
                    attempt += 1
                    delay = _backoff_delay(attempt - 1, base_delay, max_delay)
                    print(f"  {st_path.name} failed: {exc}")
                    print(f"  waiting {delay:.0f}s, retry #{attempt} until success...")
                    time.sleep(delay)
                    continue
                msg = f"{st_path.name}: {exc}"
                failures.append(msg)
                print(f"  FAILED: {exc}")
                if continue_on_error:
                    break
                raise

        if svg is None:
            continue

        svg_path.write_text(svg, encoding="utf-8")
        written.append(svg_path)
        if html:
            html_path.write_text(html_doc, encoding="utf-8")
            written.append(html_path)
        print(f"  OK: {st_path.name}")

        if request_delay > 0 and index < total:
            time.sleep(request_delay)

    if failures:
        print(f"\nAI ladder failures ({len(failures)}):")
        for msg in failures:
            print(f"  - {msg}")
    elif wait_until_success and not skip_existing:
        print(f"AI ladder complete: {total}/{total} programs")

    return written, failures
