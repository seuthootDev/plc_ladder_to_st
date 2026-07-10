from __future__ import annotations

from pathlib import Path

from .ai_ladder import render_all_ai, st_file_to_ai_ladder
from .paths import LADDER_AI_DIR, ST_DIR


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(
        description="ST -> ladder SVG/HTML via Gemini API (AI track)",
    )
    parser.add_argument("--st", help="single ST file path")
    parser.add_argument("--st-dir", default=str(ST_DIR), help="ST directory for --all")
    parser.add_argument("--out-dir", default=str(LADDER_AI_DIR), help="output directory")
    parser.add_argument("--all", action="store_true", help="convert all P*.st in st-dir")
    parser.add_argument("--no-html", action="store_true", help="skip HTML output")
    parser.add_argument("--skip-existing", action="store_true", help="skip ST files that already have SVG output")
    args = parser.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    if args.all:
        files, failures = render_all_ai(
            args.st_dir,
            out_dir,
            html=not args.no_html,
            skip_existing=args.skip_existing,
        )
        for path in files:
            print(f"Wrote {path}")
        print(f"Done: {len(files)} files -> {out_dir}")
        if failures:
            raise SystemExit(1)
        return

    if not args.st:
        parser.error("--st or --all is required")

    svg, html_doc, program = st_file_to_ai_ladder(args.st)
    base = Path(args.st).stem
    svg_path = out_dir / f"{base}.svg"
    svg_path.write_text(svg, encoding="utf-8")
    print(f"Wrote {svg_path}")
    if not args.no_html:
        html_path = out_dir / f"{base}.html"
        html_path.write_text(html_doc, encoding="utf-8")
        print(f"Wrote {html_path}")
    print(f"Program: {program.name}, rungs: {len(program.rungs)}")


if __name__ == "__main__":
    main()
