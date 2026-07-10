from __future__ import annotations

from dataclasses import dataclass

from ..models import ActionKind, BoolExpr, ProgramIR, Rung
from .registry import classify_rung, effective_condition, get_pattern, get_style, load_patterns


def build_style_rules() -> str:
    """Build AI ladder style HARD RULES from catalog.json style section."""
    s = get_style()
    label_w = s.get("rung_label_col_width", 180)
    rung_fmt = s["rung_label_format"]
    return (
        "=== CANVAS ===\n"
        "- White background (#ffffff).\n"
        f"- Left power rail ONLY at x={s['left_rail_x']}, full rung height, "
        f"stroke {s['left_rail_stroke']}, stroke-width {s['left_rail_width']}.\n"
        "- Do NOT draw a right power rail.\n"
        "- Each rung separated by a thin horizontal line (#e5e7eb, stroke-width 1).\n"
        "\n=== GRID / SPACING (fixed) ===\n"
        f"- Contact cell: {s['contact_w']} x {s['contact_h']} px.\n"
        f"- Coil cell: {s['coil_w']} x {s['coil_h']} px.\n"
        f"- Timer cell: {s['timer_w']} x {s['timer_h']} px.\n"
        f"- Horizontal gap between series elements: {s['series_gap']} px.\n"
        f"- Vertical gap between parallel OR branches: {s['branch_row_pitch']} px "
        "(contact center to center).\n"
        f"- Rung label column width: {label_w} px from left rail.\n"
        "- First rung starts at y=40; each rung block ~100-120 px tall depending on branch count.\n"
        "\n=== TYPOGRAPHY (never change) ===\n"
        "- Device labels (M202, Y20, T100, X1C ...):\n"
        f"  font-family=\"{s['font_family']}\"\n"
        f"  font-size=\"{s['font_size_device']}\" font-weight=\"bold\" fill=\"#111827\" "
        "text-anchor=\"middle\"\n"
        "  placed ABOVE the symbol center.\n"
        "- Rung labels (left column):\n"
        f"  font-family=\"{s['font_family']}\"\n"
        f"  font-size=\"{s['font_size_rung_label']}\" font-weight=\"normal\" fill=\"#111827\" "
        "text-anchor=\"start\"\n"
        f"  format exactly: \"{rung_fmt}\" using ST rung comments.\n"
        "- Program title (top):\n"
        "  font-family=\"Segoe UI, sans-serif\" font-size=\"13\" font-weight=\"bold\" "
        "fill=\"#111827\"\n"
        "  format: \"{program_name}  |  {project}\"\n"
        "\n=== WIRES ===\n"
        f"- All wires: stroke {s['wire_stroke']}, stroke-width {s['wire_width']}, "
        "stroke-linecap=\"round\", fill=\"none\".\n"
        f"- Draw junction dots (circle r={s['junction_dot_r']} fill {s['wire_stroke']}) "
        "at every T-junction / branch merge.\n"
        "\n=== CONTACTS (M, X, SM, etc.) ===\n"
        f"- NO contact: two vertical blue bars ({s['contact_color']}, stroke-width 2.5), "
        "14 px apart, height 18 px.\n"
        f"- NC contact: same bars PLUS one diagonal slash ({s['contact_color']}, stroke-width 2).\n"
        "- Horizontal wire enters left, exits right through contact center y.\n"
        "- Never use Unicode \"| |\" text as symbols; always draw geometry.\n"
        "\n=== COILS / OUTPUTS ===\n"
        f"- Coil: ellipse rx=34 ry=11, fill #fff, stroke {s['coil_color']} stroke-width 2.\n"
        "- SET coil: prefix label \"S\" before device name inside/near coil.\n"
        "- RST coil: prefix label \"R\" before device name.\n"
        f"- Timer: rounded rect, stroke {s['timer_color']}, label like \"T100\" and "
        "preset \"T#8000ms\" below or inside box.\n"
        "\n=== LOGIC LAYOUT ===\n"
        "- AND: elements in series on the same horizontal rail, left to right.\n"
        "- OR: multiple parallel horizontal rails; connect each branch to left vertical bus;\n"
        "  merge branches with a vertical bus on the right side of the OR group, then continue to coil.\n"
        "- Nested OR/AND: use additional parallel rails; never draw diagonal shortcuts.\n"
        "- One rung = one output coil/timer/set/rst at the far right of that rung "
        "(except special multi-output if ST explicitly has them).\n"
        "- Preserve ST device names exactly (M202, SM412, Y3C, /X1C for NC inputs if present in ST).\n"
        "\n=== FORBIDDEN ===\n"
        "- No CSS class-based theming that changes per rung.\n"
        "- No varying font families or sizes between rungs.\n"
        "- No decorative headers, gradients, shadows, or icons.\n"
        "- No markdown in output.\n"
        "- No right-side power rail.\n"
        "- No ASCII-art ladder text.\n"
        "\n=== OUTPUT ===\n"
        "- Output ONLY valid SVG XML: starts with <?xml or <svg, ends with </svg>.\n"
        "- Use explicit numeric coordinates (no percentage layout).\n"
        "- Group wires, symbols, labels in <g> if helpful, but keep style consistent.\n"
    )


def _count_or_branches(expr: BoolExpr) -> int:
    if expr.op == "OR":
        return len(expr.args)
    total = 0
    for arg in expr.args:
        total += _count_or_branches(arg)
    return total


def _max_and_depth(expr: BoolExpr, depth: int = 0) -> int:
    if expr.op == "AND":
        if not expr.args:
            return depth + 1
        return max(_max_and_depth(arg, depth + 1) for arg in expr.args)
    if not expr.args:
        return depth
    return max(_max_and_depth(arg, depth) for arg in expr.args)


def _expr_has_timer(expr: BoolExpr) -> bool:
    if expr.op == "CONTACT" and expr.device and expr.device.upper().startswith("T"):
        return True
    return any(_expr_has_timer(arg) for arg in expr.args)


def _expr_structure_hint(expr: BoolExpr) -> str:
    parts = [
        f"root_op={expr.op}",
        f"or_branches={_count_or_branches(expr)}",
        f"and_depth={_max_and_depth(expr)}",
    ]
    if _expr_has_timer(expr):
        parts.append("has_timer_contact=true")
    if expr.op == "NOT" or any(arg.op == "NOT" for arg in expr.args):
        parts.append("has_nc=true")
    if expr.op == "CMP_NE" or any(arg.op == "CMP_NE" for arg in expr.args):
        parts.append("has_cmp=true")
    return ", ".join(parts)


def _suggest_generic_topology(expr: BoolExpr) -> str:
    if _count_or_branches(expr) >= 2:
        return "parallel_or"
    if expr.op == "NOT":
        return "series_and (draw NC contacts for NOT wrappers)"
    return "series_and"


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
                cond = effective_condition(rung)
                suggest = _suggest_generic_topology(cond)
                structure = _expr_structure_hint(cond)
                notes = (
                    f"Unclassified rung: prefer pattern_id={suggest}. "
                    f"Structure: {structure}."
                )

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
