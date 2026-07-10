from __future__ import annotations



import json

import re

from pathlib import Path



from .generate_st import enrich_mov_destinations

from .il_builder import build_program_ir





def _extract_rungs_from_st(st_text: str) -> list[dict]:

    rungs: list[dict] = []

    pattern = re.compile(

        r"\(\* --- Rung (\d+), step (\d+)(?: \| ([^*]+?))? --- \*\)",

        re.MULTILINE,

    )

    matches = list(pattern.finditer(st_text))

    for idx, match in enumerate(matches):

        start = match.end()

        end = matches[idx + 1].start() if idx + 1 < len(matches) else st_text.find("(* --- Unsupported")

        if end < 0:

            end = st_text.find("END_PROGRAM")

        body = st_text[start:end].strip()

        rungs.append(

            {

                "rung_no": int(match.group(1)),

                "step": int(match.group(2)),

                "label": (match.group(3) or "").strip(),

                "body": body,

            }

        )

    return rungs





def verify_program(context_path: Path, st_path: Path) -> dict:

    context = json.loads(context_path.read_text(encoding="utf-8"))

    st_text = st_path.read_text(encoding="utf-8")

    rungs = _extract_rungs_from_st(st_text)



    enriched = enrich_mov_destinations(context)

    program = build_program_ir(enriched)

    expected_steps = [r.step for r in program.rungs if r.step is not None]

    st_steps = [r["step"] for r in rungs]



    missing_in_st = [s for s in expected_steps if s not in st_steps]

    extra_in_st = [s for s in st_steps if s not in expected_steps]



    return {

        "program": context.get("pou_name"),

        "expected_rungs": len(expected_steps),

        "st_rung_count": len(rungs),

        "expected_steps": expected_steps,

        "st_rung_steps": st_steps,

        "missing_steps_in_st": missing_in_st,

        "extra_steps_in_st": extra_in_st,

        "unsupported_count": len(program.unsupported),

        "unsupported_notes": program.unsupported[:10],

        "ok": not missing_in_st and not extra_in_st and len(program.unsupported) == 0,

    }





def verify_all(

    context_dir: str | Path = "plc_export/context",

    st_dir: str | Path = "plc_export/st",

) -> list[dict]:

    context_dir = Path(context_dir)

    st_dir = Path(st_dir)

    reports: list[dict] = []



    for json_path in sorted((context_dir / "programs").glob("*.json")):

        context = json.loads(json_path.read_text(encoding="utf-8"))

        st_path = st_dir / f"{context['pou_name']}.st"

        if not st_path.exists():

            reports.append({"program": context["pou_name"], "ok": False, "error": "ST file missing"})

            continue

        reports.append(verify_program(json_path, st_path))

    return reports





def main() -> None:

    import argparse



    parser = argparse.ArgumentParser(description="context vs ST rung step 대조")

    parser.add_argument("--context-dir", default="plc_export/context")

    parser.add_argument("--st-dir", default="plc_export/st")

    parser.add_argument("--program", help="특정 프로그램 번호")

    args = parser.parse_args()



    if args.program:

        ctx = Path(args.context_dir) / "programs" / f"{args.program}.json"

        context = json.loads(ctx.read_text(encoding="utf-8"))

        st = Path(args.st_dir) / f"{context['pou_name']}.st"

        report = verify_program(ctx, st)

        print(json.dumps(report, ensure_ascii=False, indent=2))

        return



    reports = verify_all(args.context_dir, args.st_dir)

    ok = sum(1 for r in reports if r.get("ok"))

    print(f"Verified: {ok}/{len(reports)} programs OK")

    for report in reports:

        status = "OK" if report.get("ok") else "CHECK"

        print(f"  [{status}] {report.get('program')}: rungs={report.get('st_rung_count')}")

        if report.get("missing_steps_in_st"):

            print(f"         missing steps: {report['missing_steps_in_st']}")

        if report.get("unsupported_count"):

            print(f"         unsupported: {report['unsupported_count']}")





if __name__ == "__main__":

    main()

