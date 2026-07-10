from __future__ import annotations

import csv
import io
import re
from pathlib import Path

from .models import IlInstruction

DEVICE_IN_OPERAND = re.compile(
    r"\b(?:SM|SD|X|Y|M|L|D|T|C|V|Z)\d+(?:\.\d+|[A-F])?\b",
    re.IGNORECASE,
)


def _strip_quotes(value: str) -> str:
    return value.strip().strip('"')


def _normalize_device(device: str) -> str:
    return device.upper().replace(" ", "")


def parse_il_csv(path: str | Path) -> tuple[str, str, list[IlInstruction], list[str]]:
    """Parse GX Works2 instruction list CSV (UTF-16 tab-separated)."""
    path = Path(path)
    raw_bytes = path.read_bytes()
    if raw_bytes[:2] in (b"\xff\xfe", b"\xfe\xff"):
        text = raw_bytes.decode("utf-16")
    else:
        text = raw_bytes.decode("utf-8-sig")

    project = ""
    cpu = ""
    instructions: list[IlInstruction] = []
    line_labels: list[str] = []
    pending_label = ""

    with io.StringIO(text) as handle:
        reader = csv.reader(handle, delimiter="\t")
        for line_no, raw in enumerate(reader, start=1):
            if not raw:
                continue
            cells = [_strip_quotes(c) for c in raw]

            if line_no == 1 and cells and not cells[0].startswith("Step"):
                project = cells[0]
                continue
            if len(cells) >= 2 and cells[0] == "PLC Information:":
                cpu = cells[1] if len(cells) > 1 else ""
                continue
            if cells[0] == "Step No.":
                continue

            step_s, line_stmt, inst, device, *_rest = (cells + ["", "", "", ""])[:4]
            step = int(step_s) if step_s.isdigit() else None

            if line_stmt and not inst:
                pending_label = line_stmt
                if step is not None:
                    line_labels.append(f"{step}:{line_stmt}")
                continue

            if not inst:
                if instructions and device:
                    last = instructions[-1]
                    if last.mnemonic == "OUT" and device[0].upper() == "K":
                        last.preset = device.upper()
                    elif last.mnemonic == "MOV" and not last.mov_dest:
                        last.mov_dest = _normalize_device(device)
                continue

            label = pending_label
            pending_label = ""
            instructions.append(
                IlInstruction(
                    step=step,
                    label=label,
                    mnemonic=inst.upper(),
                    operand=_normalize_device(device) if device else "",
                )
            )
            if inst.upper() == "END":
                break

    return project, cpu, instructions, line_labels


def collect_devices_from_instructions(instructions: list[IlInstruction]) -> list[str]:
    seen: list[str] = []
    for inst in instructions:
        for token in DEVICE_IN_OPERAND.findall(inst.operand):
            norm = _normalize_device(token)
            if norm not in seen:
                seen.append(norm)
        if inst.mnemonic == "OUT" and inst.preset:
            preset = inst.preset.upper()
            if preset not in seen:
                seen.append(preset)
    return seen


def lookup_comment(device: str, comments: dict[str, str]) -> str:
    """Match D110.8 style devices to word-level D110 comment if needed."""
    device = _normalize_device(device)
    if device in comments:
        return comments[device]

    if "." in device:
        word = device.split(".", 1)[0]
        if word in comments:
            return comments[word]

    match = re.match(r"^([A-Z]+\d+)", device)
    if match and match.group(1) in comments:
        return comments[match.group(1)]
    return ""
