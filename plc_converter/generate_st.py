from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .csv_parser import parse_il_csv
from .il_builder import build_program_ir
from .st_generator import generate_st, generate_st_parts


def enrich_mov_destinations(context: dict) -> dict:
    """Fill MOV destination from CSV continuation rows if missing in context JSON."""
    csv_path = context.get("csv_path")
    if not csv_path or not Path(csv_path).exists():
        return context

    _, _, instructions, _ = parse_il_csv(csv_path)
    mov_by_step = {
        inst.step: inst.mov_dest
        for inst in instructions
        if inst.mnemonic == "MOV" and inst.mov_dest
    }

    enriched = dict(context)
    new_instructions: list[dict[str, Any]] = []
    for inst in context.get("instructions", []):
        item = dict(inst)
        if item.get("mnemonic") == "MOV" and not item.get("mov_dest"):
            dest = mov_by_step.get(item.get("step"))
            if dest:
                item["mov_dest"] = dest
        new_instructions.append(item)
    enriched["instructions"] = new_instructions
    return enriched


def context_to_st(context: dict, *, target: str = "codesys", pou_name: str | None = None) -> str:
    enriched = enrich_mov_destinations(context)
    program = build_program_ir(enriched)
    return generate_st(program, enriched, target=target, pou_name=pou_name)


def generate_all(
    context_dir: str | Path = "plc_export/context",
    output_dir: str | Path = "plc_export/st",
    *,
    target: str = "codesys",
    pou_name: str | None = None,
) -> list[Path]:
    context_dir = Path(context_dir)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []

    for json_path in sorted((context_dir / "programs").glob("*.json")):
        context = json.loads(json_path.read_text(encoding="utf-8"))
        enriched = enrich_mov_destinations(context)
        program = build_program_ir(enriched)
        st_text = generate_st(program, enriched, target=target, pou_name=pou_name)
        out = output_dir / f"{context['pou_name']}.st"
        out.write_text(st_text, encoding="utf-8")
        written.append(out)

        if target == "codesys":
            decl, impl = generate_st_parts(program, enriched, pou_name=pou_name)
            decl_dir = output_dir / "codesys"
            decl_dir.mkdir(parents=True, exist_ok=True)
            suffix = f".{pou_name}" if pou_name else ""
            base = f"{context['pou_name']}{suffix}"
            (decl_dir / f"{base}.declaration.st").write_text(decl, encoding="utf-8")
            (decl_dir / f"{base}.implementation.st").write_text(impl, encoding="utf-8")
    return written


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="context JSON -> ST 파일 생성")
    parser.add_argument(
        "--context-dir",
        default="plc_export/context",
        help="context JSON 폴더",
    )
    parser.add_argument(
        "--out-dir",
        default="plc_export/st",
        help="ST 출력 폴더",
    )
    parser.add_argument(
        "--program",
        help="특정 프로그램 번호만 (예: 99)",
    )
    parser.add_argument(
        "--format",
        choices=("codesys", "generic"),
        default="codesys",
        help="codesys: no PROGRAM/END_PROGRAM (default); generic: full PROGRAM wrapper",
    )
    parser.add_argument(
        "--pou-name",
        help="CODESYS POU 객체 이름 (예: PLC_PRG). Declaration의 PROGRAM 이름과 일치시킴",
    )
    args = parser.parse_args()

    if args.program:
        json_path = Path(args.context_dir) / "programs" / f"{args.program}.json"
        context = json.loads(json_path.read_text(encoding="utf-8"))
        print(context_to_st(context, target=args.format, pou_name=args.pou_name))
        return

    files = generate_all(args.context_dir, args.out_dir, target=args.format, pou_name=args.pou_name)
    for path in files:
        print(f"Wrote {path}")
    print(f"Done: {len(files)} ST files")


if __name__ == "__main__":
    main()
