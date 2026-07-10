from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import Any

from .csv_parser import collect_devices_from_instructions, lookup_comment, parse_il_csv
from .device_utils import device_to_st_name, infer_data_type, preset_to_ms
from .models import ProgramContext, VarHint
from .pdf_parser import PdfProjectData, parse_pdf_text
from .pdf_reader import resolve_pdf_source

PROGRAM_SLUGS = {
    "01": "Main",
    "02": "Lamp",
    "10": "PrimerVision",
    "11": "SealerVision",
    "12": "BodyVision",
    "20": "PrimerRobot",
    "21": "BodyRobot",
    "30": "Centering",
    "31": "Sealer",
    "32": "Primer",
    "33": "Gripper",
    "99": "Error",
}


def pou_name(program_no: str, program_name: str | None = None) -> str:
    slug = PROGRAM_SLUGS.get(program_no, program_name or program_no)
    safe = "".join(ch for ch in slug if ch.isalnum())
    return f"P{program_no}_{safe}"


def _write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def build_program_context(
    program_no: str,
    program_name: str,
    csv_path: Path,
    pdf_data: PdfProjectData,
) -> ProgramContext:
    project, cpu, instructions, line_labels = parse_il_csv(csv_path)
    devices_used = collect_devices_from_instructions(instructions)

    device_comments = {
        dev: lookup_comment(dev, pdf_data.device_comments)
        for dev in devices_used
        if lookup_comment(dev, pdf_data.device_comments)
    }

    timer_presets = pdf_data.timer_presets_by_program.get(program_no, [])
    timer_base = pdf_data.timer_low_speed_ms or 100

    var_hints: list[VarHint] = []
    for dev in devices_used:
        comment = lookup_comment(dev, pdf_data.device_comments)
        var_hints.append(
            VarHint(
                device=dev,
                comment=comment,
                data_type=infer_data_type(dev),
                st_name=device_to_st_name(dev),
            )
        )

    ladder_devices = pdf_data.ladder_devices_by_program.get(program_no, [])

    return ProgramContext(
        program_no=program_no,
        program_name=program_name,
        pou_name=pou_name(program_no, program_name),
        project=project,
        cpu=cpu,
        csv_path=str(csv_path).replace("\\", "/"),
        line_labels=[
            {"step": int(item.split(":", 1)[0]), "label": item.split(":", 1)[1]}
            for item in line_labels
            if ":" in item
        ],
        instructions=[
            {
                "step": inst.step,
                "label": inst.label,
                "mnemonic": inst.mnemonic,
                "operand": inst.operand,
                "preset": inst.preset,
                "preset_ms": preset_to_ms(inst.preset, timer_base) if inst.preset else None,
                "mov_dest": inst.mov_dest,
            }
            for inst in instructions
        ],
        devices_used=devices_used,
        device_comments=device_comments,
        timer_presets=[asdict(tp) for tp in timer_presets],
        var_hints=[asdict(vh) for vh in var_hints],
        ladder_devices=ladder_devices,
    )


def prepare_context_files(
    *,
    pdf_path: str | Path | None = None,
    csv_dir: str | Path = "csv",
    output_dir: str | Path = "plc_export/context",
    fallback_txt: str | Path | None = "12314_extracted.txt",
) -> dict[str, Any]:
    """Read PDF + CSV and write intermediate JSON files for ST generation."""
    source_path, pdf_text = resolve_pdf_source(pdf_path, fallback_txt=fallback_txt)
    pdf_data = parse_pdf_text(pdf_text)

    csv_dir = Path(csv_dir)
    output_dir = Path(output_dir)
    programs_dir = output_dir / "programs"
    programs_dir.mkdir(parents=True, exist_ok=True)

    program_map = {p.program_no: p.name for p in pdf_data.programs}

    project_info = {
        "source_pdf": str(source_path).replace("\\", "/"),
        "project_title": pdf_data.project_title,
        "timer_low_speed_ms": pdf_data.timer_low_speed_ms,
        "timer_high_speed_ms": pdf_data.timer_high_speed_ms,
        "programs": [asdict(p) for p in pdf_data.programs],
    }
    _write_json(output_dir / "project.json", project_info)
    _write_json(output_dir / "device_comments.json", pdf_data.device_comments)
    _write_json(
        output_dir / "timer_presets.json",
        {k: [asdict(tp) for tp in v] for k, v in pdf_data.timer_presets_by_program.items()},
    )

    written_programs: list[str] = []
    for csv_path in sorted(csv_dir.glob("*.csv")):
        program_no = csv_path.stem
        program_name = program_map.get(program_no, PROGRAM_SLUGS.get(program_no, program_no))
        ctx = build_program_context(program_no, program_name, csv_path, pdf_data)
        out_path = programs_dir / f"{program_no}.json"
        _write_json(out_path, ctx.to_dict())
        written_programs.append(program_no)

    manifest = {
        "version": "0.1.0",
        "source_pdf": str(source_path).replace("\\", "/"),
        "csv_dir": str(csv_dir).replace("\\", "/"),
        "output_dir": str(output_dir).replace("\\", "/"),
        "program_count": len(written_programs),
        "programs": written_programs,
        "device_comment_count": len(pdf_data.device_comments),
        "next_step": "Use plc_export/context/programs/*.json as input for ST generator",
    }
    _write_json(output_dir / "manifest.json", manifest)
    return manifest


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(
        description="GX Works2 PDF + IL CSV → ST 생성용 중간 JSON 파일 준비",
    )
    parser.add_argument(
        "--pdf",
        help="Project Listing PDF (없으면 12314_extracted.txt 사용)",
        default=None,
    )
    parser.add_argument("--csv-dir", default="csv", help="IL CSV 폴더")
    parser.add_argument(
        "--out-dir",
        default="plc_export/context",
        help="출력 폴더 (default: plc_export/context)",
    )
    parser.add_argument(
        "--fallback-txt",
        default="12314_extracted.txt",
        help="PDF 없을 때 사용할 추출 텍스트",
    )
    args = parser.parse_args()

    manifest = prepare_context_files(
        pdf_path=args.pdf,
        csv_dir=args.csv_dir,
        output_dir=args.out_dir,
        fallback_txt=args.fallback_txt,
    )
    print(f"Source: {manifest['source_pdf']}")
    print(f"Wrote {manifest['program_count']} program context files → {args.out_dir}")
    for no in manifest["programs"]:
        slug = PROGRAM_SLUGS.get(no, no)
        print(f"  programs/{no}.json  (P{no}_{slug})")
    print(f"Device comments: {manifest['device_comment_count']}")


if __name__ == "__main__":
    main()
