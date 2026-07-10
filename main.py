"""Run the full PLC pipeline: prepare -> ST -> verify -> ladder."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from plc_converter.generate_st import generate_all
from plc_converter.paths import CONTEXT_DIR, CSV_DIR, LADDER_AI_DIR, LADDER_DIR, ST_DIR
from plc_converter.prepare import prepare_context_files
from plc_converter.render_ladder import render_all
from plc_converter.ai_ladder import render_all_ai
from plc_converter.verify import verify_all


def run_pipeline(*, skip_verify: bool = False, html: bool = True, ai_ladder: bool = False, ai_skip_existing: bool = False) -> int:
    print("== 1/4 prepare ==")
    manifest = prepare_context_files(
        csv_dir=CSV_DIR,
        output_dir=CONTEXT_DIR,
    )
    print(f"Source: {manifest['source_pdf']}")
    print(f"Wrote {manifest['program_count']} program context files")

    print("\n== 2/4 generate_st ==")
    st_files = generate_all(CONTEXT_DIR, ST_DIR)
    for path in st_files:
        print(f"Wrote {path}")
    print(f"Done: {len(st_files)} ST files")

    if not skip_verify:
        print("\n== 3/4 verify ==")
        reports = verify_all(CONTEXT_DIR, ST_DIR)
        ok = sum(1 for r in reports if r.get("ok"))
        print(f"Verified: {ok}/{len(reports)} programs OK")
        for report in reports:
            status = "OK" if report.get("ok") else "CHECK"
            print(f"  [{status}] {report.get('program')}: rungs={report.get('st_rung_count')}")
        if ok != len(reports):
            return 1
    else:
        print("\n== 3/4 verify (skipped) ==")

    print("\n== 4/4 render_ladder (logic track) ==")
    ladder_files = render_all(ST_DIR, LADDER_DIR, html=html)
    for path in ladder_files:
        print(f"Wrote {path}")
    print(f"Done: {len(ladder_files)} ladder files -> {LADDER_DIR}")

    if ai_ladder:
        print("\n== 5/5 render_ladder_ai (AI track) ==")
        try:
            ai_files, ai_failures = render_all_ai(
                ST_DIR,
                LADDER_AI_DIR,
                html=html,
                skip_existing=ai_skip_existing,
            )
        except (RuntimeError, ImportError) as exc:
            print(f"AI ladder failed: {exc}")
            return 1
        for path in ai_files:
            print(f"Wrote {path}")
        print(f"Done: {len(ai_files)} AI ladder files -> {LADDER_AI_DIR}")
        if ai_failures:
            print(f"Warning: {len(ai_failures)} AI file(s) failed")
            return 1

    return 0


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="PLC pipeline: prepare -> ST -> verify -> ladder")
    parser.add_argument("--skip-verify", action="store_true", help="verify 단계 생략")
    parser.add_argument("--no-html", action="store_true", help="HTML 생성 생략 (SVG만)")
    parser.add_argument(
        "--ai-ladder",
        action="store_true",
        help="Gemini API로 ST->래더 AI track 추가 생성 (plc_export/ladder_ai/)",
    )
    parser.add_argument(
        "--ai-skip-existing",
        action="store_true",
        help="AI track: 이미 생성된 SVG는 건너뛰기 (재시도용)",
    )
    args = parser.parse_args()
    raise SystemExit(
        run_pipeline(
            skip_verify=args.skip_verify,
            html=not args.no_html,
            ai_ladder=args.ai_ladder,
            ai_skip_existing=args.ai_skip_existing,
        )
    )


if __name__ == "__main__":
    main()