from __future__ import annotations

from dataclasses import dataclass

from ..models import ActionKind, ProgramIR, Rung
from .registry import classify_rung, effective_condition, get_pattern, load_patterns


@dataclass(frozen=True)
class RungPatternAssignment:
    rung_index: int
    step: int | None
    label: str
    pattern_id: str
    pattern_name: str
    topology: str
    bool_shape: str
    notes: str
    condition: str
    outputs: str


def _format_outputs(rung: Rung) -> str:
    parts: list[str] = []
    for action in rung.actions:
        if action.kind == ActionKind.OUT:
            parts.append(action.target)
        elif action.kind == ActionKind.SET:
            parts.append(f"SET {action.target}")
        elif action.kind == ActionKind.RST:
            parts.append(f"RST {action.target}")
        elif action.kind == ActionKind.TON_COIL:
            preset = action.preset or (f"T#{action.preset_ms}ms" if action.preset_ms else "")
            parts.append(f"{action.target} {preset}".strip())
        elif action.kind == ActionKind.MOV:
            parts.append(f"MOV {action.mov_source} -> {action.mov_dest}")
        else:
            parts.append(str(action.kind.value))
    return ", ".join(parts) if parts else "(none)"


def _fallback_pattern(pattern_id: str):
    if pattern_id == "generic":
        return get_pattern("parallel_or") or get_pattern("series_and")
    return get_pattern(pattern_id)


def build_rung_assignments(program: ProgramIR) -> list[RungPatternAssignment]:
    rows: list[RungPatternAssignment] = []
    for index, rung in enumerate(program.rungs, start=1):
        pattern_id = classify_rung(rung)
        pattern = _fallback_pattern(pattern_id)
        if pattern is None:
            pattern_name = pattern_id
            topology = "left rail -> condition -> output"
            bool_shape = "unknown"
            notes = "No catalog match; keep standard style rules."
        else:
            pattern_name = pattern.name if pattern_id != "generic" else "generic (use series_and or parallel_or)"
            topology = pattern.topology
            bool_shape = pattern.bool_shape
            notes = pattern.notes
            if pattern_id == "generic":
                notes = "Unclassified rung: if OR branches exist use parallel_or topology, else series_and."

        rows.append(
            RungPatternAssignment(
                rung_index=index,
                step=rung.step,
                label=rung.label,
                pattern_id=pattern_id,
                pattern_name=pattern_name,
                topology=topology,
                bool_shape=bool_shape,
                notes=notes,
                condition=effective_condition(rung).to_st(),
                outputs=_format_outputs(rung),
            )
        )
    return rows


def _format_pattern_library(used_ids: list[str]) -> str:
    lines = ["Pattern library (reference for assigned pattern_id values):"]
    for pattern in load_patterns():
        if pattern.id not in used_ids and pattern.id != "generic":
            continue
        lines.append(f"- {pattern.id}: {pattern.name}")
        lines.append(f"  bool_shape: {pattern.bool_shape}")
        lines.append(f"  topology: {pattern.topology}")
        lines.append(f"  notes: {pattern.notes}")
        if pattern.pdf_examples:
            ex = pattern.pdf_examples[0]
            lines.append(
                "  pdf_example: {program} rung {rung} step {step}".format(
                    program=ex.get("program", "?"),
                    rung=ex.get("rung", "?"),
                    step=ex.get("step", "?"),
                )
            )
    return "\n".join(lines)


def build_pattern_guide(program: ProgramIR) -> str:
    assignments = build_rung_assignments(program)
    used_ids = sorted({a.pattern_id for a in assignments if a.pattern_id != "generic"})

    lines = [
        "=== RUNG PATTERN ASSIGNMENTS (MANDATORY) ===",
        "Draw each rung using ONLY the assigned pattern_id topology below.",
        "Do NOT invent a different branch layout when a pattern_id is given.",
        "Devices and logic values must come from ST; geometry must follow the template topology.",
        "",
    ]

    for item in assignments:
        step = item.step if item.step is not None else "-"
        lines.extend(
            [
                f"Rung {item.rung_index} (step {step}) -> pattern_id={item.pattern_id} ({item.pattern_name})",
                f"  label: {item.label or '-'}",
                f"  condition: {item.condition}",
                f"  outputs: {item.outputs}",
                f"  bool_shape: {item.bool_shape}",
                f"  topology:",
                f"    {item.topology}",
                f"  notes: {item.notes}",
                "",
            ]
        )

    if used_ids:
        lines.append(_format_pattern_library(used_ids))
    else:
        lines.append("Pattern library: all rungs generic; apply series_and or parallel_or topology.")

    return "\n".join(lines)
