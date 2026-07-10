from __future__ import annotations

from pathlib import Path

from .paths import PDF_CANDIDATES, PROJECT_ROOT


def load_pdf_text(path: str | Path) -> str:
    """Extract plain text from a GX Works2 Project Listing PDF."""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(path)

    suffix = path.suffix.lower()
    if suffix == ".txt":
        return path.read_text(encoding="utf-8", errors="replace")

    if suffix == ".pdf":
        try:
            import fitz  # pymupdf
        except ImportError as exc:
            raise ImportError(
                "PDF 읽기에 pymupdf가 필요합니다: pip install pymupdf"
            ) from exc

        pages: list[str] = []
        with fitz.open(path) as doc:
            for page in doc:
                pages.append(page.get_text("text"))
        return "\n".join(pages)

    raise ValueError(f"지원하지 않는 형식입니다: {path}")


def resolve_pdf_source(
    pdf_path: str | Path | None,
    *,
    fallback_txt: str | Path | None = None,
) -> tuple[Path, str]:
    """Pick PDF or pre-extracted text file."""
    candidates: list[Path] = []
    if pdf_path:
        candidates.append(Path(pdf_path))
        if not candidates[-1].is_absolute():
            candidates.append(PROJECT_ROOT / pdf_path)
    if fallback_txt:
        candidates.append(Path(fallback_txt))
        if not candidates[-1].is_absolute():
            candidates.append(PROJECT_ROOT / fallback_txt)

    candidates.extend(PDF_CANDIDATES)

    for candidate in candidates:
        if candidate.exists():
            return candidate, load_pdf_text(candidate)

    searched = ", ".join(str(c) for c in candidates if c)
    raise FileNotFoundError(
        f"PDF 또는 추출 텍스트를 찾을 수 없습니다. 확인: {searched}"
    )
