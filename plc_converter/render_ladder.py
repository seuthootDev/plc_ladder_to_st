from __future__ import annotations

import json
from pathlib import Path

from .generate_st import enrich_mov_destinations
from .il_builder import build_program_ir
from .ladder_layout import layout_program
from .ladder_renderer import render_html, render_svg
from .st_parser import parse_st_file


def st_file_to_ladder(st_path: str | Path) -> tuple[str, str]:
    program = parse_st_file(st_path)
    layout = layout_program(program)
    svg = render_svg(layout, program)
    html_doc = render_html(layout, program, svg)
    return svg, html_doc


def context_to_ladder(context: dict) -> tuple[str, str]:
    enriched = enrich_mov_destinations(context)
    program = build_program_ir(enriched)
    layout = layout_program(program)
    svg = render_svg(layout, program)
    html_doc = render_html(layout, program, svg)
    return svg, html_doc


def render_all(
    st_dir: str | Path = "plc_export/st",
    output_dir: str | Path = "plc_export/ladder",
    *,
    html: bool = True,
) -> list[Path]:
    st_dir = Path(st_dir)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []

    for st_path in sorted(st_dir.glob("P*.st")):
        svg, html_doc = st_file_to_ladder(st_path)
        svg_path = output_dir / f"{st_path.stem}.svg"
        svg_path.write_text(svg, encoding="utf-8")
        written.append(svg_path)
        if html:
            html_path = output_dir / f"{st_path.stem}.html"
            html_path.write_text(html_doc, encoding="utf-8")
            written.append(html_path)
    return written


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="ST 파일 -> 래더 SVG/HTML 뷰어 생성")
    parser.add_argument("--st", help="ST 파일 경로")
    parser.add_argument("--context", help="context JSON 경로 (ST 대신 IR 직접 생성)")
    parser.add_argument("--program", help="context programs/XX.json 번호 (예: 01)")
    parser.add_argument("--context-dir", default="plc_export/context")
    parser.add_argument("--st-dir", default="plc_export/st")
    parser.add_argument("--out-dir", default="plc_export/ladder")
    parser.add_argument("--all", action="store_true", help="st-dir 아래 P*.st 전체 변환")
    parser.add_argument("--no-html", action="store_true", help="HTML 생성 생략")
    args = parser.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    if args.all:
        files = render_all(args.st_dir, out_dir, html=not args.no_html)
        for path in files:
            print(f"Wrote {path}")
        print(f"Done: {len(files)} files")
        return

    if args.context:
        context = json.loads(Path(args.context).read_text(encoding="utf-8"))
        svg, html_doc = context_to_ladder(context)
        base = context.get("pou_name", "program")
    elif args.program:
        json_path = Path(args.context_dir) / "programs" / f"{args.program}.json"
        context = json.loads(json_path.read_text(encoding="utf-8"))
        svg, html_doc = context_to_ladder(context)
        base = context.get("pou_name", f"P{args.program}")
    elif args.st:
        svg, html_doc = st_file_to_ladder(args.st)
        base = Path(args.st).stem
    else:
        parser.error("--st, --program, --context, 또는 --all 중 하나를 지정하세요")

    svg_path = out_dir / f"{base}.svg"
    svg_path.write_text(svg, encoding="utf-8")
    print(f"Wrote {svg_path}")
    if not args.no_html:
        html_path = out_dir / f"{base}.html"
        html_path.write_text(html_doc, encoding="utf-8")
        print(f"Wrote {html_path}")


if __name__ == "__main__":
    main()
