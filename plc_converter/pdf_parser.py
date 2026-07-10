from __future__ import annotations

import re
from dataclasses import dataclass, field

from .models import ProgramInfo, TimerPreset

DEVICE_TOKEN = re.compile(
    r"\b(?:SM|SD|X|Y|M|L|D|T|C|V|Z)\d+(?:\.\d+|[A-F])?\b",
    re.IGNORECASE,
)
COMMENT_LINE = re.compile(
    r"^([A-Z]+\d+(?:\.\d+|[A-F])?)\s+(.+?)\s*$",
    re.IGNORECASE,
)
PROGRAM_BLOCK = re.compile(
    r"^(\d{2})\s*\n\[([^\]]+)\]\s*\n",
    re.MULTILINE,
)
SCAN_PROGRAM_LINE = re.compile(
    r"^Scan Program (\d{2})\s*\n\[([^\]]+)\]",
    re.MULTILINE,
)
TC_SETTING_BLOCK = re.compile(
    r"TC Setting.*?\nData Name : (\d{2})\s*\n"
    r"Position Device Setting Value\s*\n(.*?)(?=\n\d+\s*\nTC Setting|\nDevice List|\Z)",
    re.DOTALL,
)
TIMER_LINE = re.compile(
    r"\(\s*(\d+)\)\s+(T\d+)\s+(K\d+)",
    re.IGNORECASE,
)
LOW_SPEED_TIMER = re.compile(r"Low Speed\s+(\d+)\s*ms", re.IGNORECASE)
HIGH_SPEED_TIMER = re.compile(r"High-Speed\s+([\d.]+)\s*ms", re.IGNORECASE)


@dataclass
class PdfProjectData:
    project_title: str = ""
    timer_low_speed_ms: int | None = None
    timer_high_speed_ms: float | None = None
    programs: list[ProgramInfo] = field(default_factory=list)
    device_comments: dict[str, str] = field(default_factory=dict)
    timer_presets_by_program: dict[str, list[TimerPreset]] = field(default_factory=dict)
    ladder_devices_by_program: dict[str, list[str]] = field(default_factory=dict)


def _normalize_device(device: str) -> str:
    return device.upper().replace(" ", "")


def parse_programs(text: str) -> list[ProgramInfo]:
    """Parse program list from GX Works2 Project Listing PDF text."""
    programs: dict[str, ProgramInfo] = {}
    known = {"01", "02", "10", "11", "12", "20", "21", "30", "31", "32", "33", "99"}

    start = text.find("Program setting")
    section = text[start : start + 4000] if start >= 0 else text
    lines = [ln.strip() for ln in section.splitlines()]

    i = 0
    while i < len(lines):
        line = lines[i]
        if line.startswith("Scan Program "):
            no = line.replace("Scan Program ", "").strip()
            if i + 1 < len(lines):
                name_match = re.match(r"^\[([^\]]+)\]$", lines[i + 1])
                if name_match and no in known:
                    programs[no] = ProgramInfo(
                        program_no=no,
                        name=name_match.group(1).strip(),
                        execute_type="Scan",
                    )
                    i += 2
                    continue
        if re.fullmatch(r"\d{2}", line) and line in known:
            if i + 1 < len(lines):
                name_match = re.match(r"^\[([^\]]+)\]$", lines[i + 1])
                if name_match:
                    programs[line] = ProgramInfo(
                        program_no=line,
                        name=name_match.group(1).strip(),
                        execute_type="Scan",
                    )
                    i += 2
                    continue
        i += 1

    if not programs:
        for match in SCAN_PROGRAM_LINE.finditer(text):
            no, name = match.group(1), match.group(2).strip()
            if no in known:
                programs[no] = ProgramInfo(program_no=no, name=name, execute_type="Scan")
        for match in PROGRAM_BLOCK.finditer(text):
            no, name = match.group(1), match.group(2).strip()
            if no in known:
                programs[no] = ProgramInfo(program_no=no, name=name, execute_type="Scan")

    return [programs[k] for k in sorted(programs)]


def parse_device_comments(text: str) -> dict[str, str]:
    start = text.find("Device Comment")
    if start < 0:
        return {}

    section = text[start:]
    end_markers = ("Device Memory", "Device List", "Change History")
    end = len(section)
    for marker in end_markers:
        pos = section.find(marker)
        if pos > 0:
            end = min(end, pos)
    section = section[:end]

    comments: dict[str, str] = {}
    for line in section.splitlines():
        line = line.strip()
        if not line or line.startswith("Device"):
            continue
        match = COMMENT_LINE.match(line)
        if not match:
            continue
        device = _normalize_device(match.group(1))
        comment = match.group(2).strip()
        if comment and not comment.startswith("0d "):
            comments[device] = comment
    return comments


def parse_timer_presets(text: str) -> dict[str, list[TimerPreset]]:
    presets: dict[str, list[TimerPreset]] = {}
    for match in TC_SETTING_BLOCK.finditer(text):
        program_no = match.group(1)
        body = match.group(2)
        items: list[TimerPreset] = []
        for line in body.splitlines():
            tm = TIMER_LINE.search(line)
            if tm:
                items.append(
                    TimerPreset(
                        step=int(tm.group(1)),
                        timer=_normalize_device(tm.group(2)),
                        preset=tm.group(3).upper(),
                    )
                )
        if items:
            presets[program_no] = items
    return presets


def parse_ladder_devices_by_program(text: str) -> dict[str, list[str]]:
    """Collect device tokens appearing on each program's ladder pages."""
    result: dict[str, list[str]] = {}
    pattern = re.compile(
        r"Ladder.*?\nData Name : (\d{2})\s*\n.*?(?=Ladder.*?\nData Name : |\nDevice Comment|\Z)",
        re.DOTALL,
    )
    for match in pattern.finditer(text):
        program_no = match.group(1)
        block = match.group(0)
        seen: list[str] = []
        for token in DEVICE_TOKEN.findall(block):
            norm = _normalize_device(token)
            if norm not in seen:
                seen.append(norm)
        if seen:
            existing = result.setdefault(program_no, [])
            for dev in seen:
                if dev not in existing:
                    existing.append(dev)
    return result


def parse_plc_parameters(text: str) -> tuple[int | None, float | None]:
    low = LOW_SPEED_TIMER.search(text)
    high = HIGH_SPEED_TIMER.search(text)
    low_ms = int(low.group(1)) if low else None
    high_ms = float(high.group(1)) if high else None
    return low_ms, high_ms


def parse_pdf_text(text: str) -> PdfProjectData:
    title = ""
    first_lines = [ln.strip() for ln in text.splitlines()[:5] if ln.strip()]
    if first_lines:
        title = first_lines[0]

    low_ms, high_ms = parse_plc_parameters(text)
    return PdfProjectData(
        project_title=title,
        timer_low_speed_ms=low_ms,
        timer_high_speed_ms=high_ms,
        programs=parse_programs(text),
        device_comments=parse_device_comments(text),
        timer_presets_by_program=parse_timer_presets(text),
        ladder_devices_by_program=parse_ladder_devices_by_program(text),
    )
