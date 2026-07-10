from __future__ import annotations

from .models import ActionKind, BoolExpr, ProgramIR, Rung, RungAction, st_name


def _ms_to_time_literal(ms: int | None) -> str:
    if ms is None:
        return "T#0ms"
    if ms % 1000 == 0:
        return f"T#{ms // 1000}s"
    return f"T#{ms}ms"


def _comment(text: str) -> str:
    if not text:
        return ""
    return f" (* {text.strip()} *)"


def _collect_expr_names(expr: BoolExpr | None) -> set[str]:
    if expr is None:
        return set()
    names: set[str] = set()
    if expr.op == "CONTACT":
        names.add(st_name(expr.device))
    for arg in expr.args:
        names |= _collect_expr_names(arg)
    return names


def _collect_pulse_vars(program: ProgramIR) -> set[str]:
    pulse: set[str] = set()
    for rung in program.rungs:
        for name in _collect_expr_names(rung.condition):
            if name.endswith("_PLS"):
                pulse.add(name)
        for action in rung.actions:
            for name in _collect_expr_names(action.condition):
                if name.endswith("_PLS"):
                    pulse.add(name)
    return pulse


def _emit_var_block(
    var_hints: list[dict],
    device_comments: dict[str, str],
    extra_bool_names: set[str] | None = None,
) -> list[str]:
    lines = ["VAR"]
    seen: set[str] = set()
    for hint in var_hints:
        dtype = hint.get("data_type", "BOOL")
        if dtype in {"CONST"}:
            continue
        name = hint.get("st_name") or st_name(hint.get("device", ""))
        if name in seen:
            continue
        seen.add(name)
        comment = hint.get("comment") or device_comments.get(hint.get("device", ""), "")
        if dtype == "TON":
            lines.append(f"    {name} : TON;{_comment(comment)}")
        elif dtype == "CTU":
            lines.append(f"    {name} : CTU;{_comment(comment)}")
        elif dtype == "WORD":
            lines.append(f"    {name} : WORD;{_comment(comment)}")
        else:
            lines.append(f"    {name} : BOOL;{_comment(comment)}")
    for name in sorted(extra_bool_names or []):
        if name in seen:
            continue
        seen.add(name)
        base = name[:-4] if name.endswith("_PLS") else name
        comment = device_comments.get(base, "LDP pulse edge")
        lines.append(f"    {name} : BOOL;{_comment(comment)}")
    lines.append("END_VAR")
    return lines


def _emit_bool_action(action: RungAction) -> list[str]:
    target = st_name(action.target)
    cond = (action.condition or BoolExpr(op="TRUE")).to_st()
    lines: list[str] = []

    if action.kind == ActionKind.OUT:
        lines.append(f"IF {cond} THEN")
        lines.append(f"    {target} := TRUE;")
        lines.append("ELSE")
        lines.append(f"    {target} := FALSE;")
        lines.append("END_IF;")
    elif action.kind == ActionKind.SET:
        lines.append(f"IF {cond} THEN")
        lines.append(f"    {target} := TRUE;")
        lines.append("END_IF;")
    elif action.kind == ActionKind.RST:
        lines.append(f"IF {cond} THEN")
        lines.append(f"    {target} := FALSE;")
        lines.append("END_IF;")
    return lines


def _emit_ton_action(action: RungAction) -> list[str]:
    target = st_name(action.target)
    cond = (action.condition or BoolExpr(op="TRUE")).to_st()
    pt = _ms_to_time_literal(action.preset_ms)
    lines = [
        f"IF {cond} THEN",
        f"    {target}(IN := TRUE, PT := {pt});",
        "ELSE",
        f"    {target}(IN := FALSE);",
        "END_IF;",
    ]
    if action.preset and action.preset_ms is None:
        lines.insert(0, f"(* TODO: timer preset {action.preset} *)")
    return lines


def _emit_mov_action(action: RungAction) -> list[str]:
    cond = (action.condition or BoolExpr(op="TRUE")).to_st()
    src = st_name(action.mov_source)
    dst = st_name(action.mov_dest or action.target)
    if not action.mov_dest:
        return [f"(* TODO: MOV {action.mov_source} -> ? IF {cond} *)"]
    return [
        f"IF {cond} THEN",
        f"    {dst} := {src};",
        "END_IF;",
    ]


def _emit_action(action: RungAction) -> list[str]:
    if action.kind == ActionKind.TON_COIL:
        return _emit_ton_action(action)
    if action.kind == ActionKind.MOV:
        return _emit_mov_action(action)
    return _emit_bool_action(action)


def _emit_implementation(program: ProgramIR) -> list[str]:
    lines: list[str] = []
    for i, rung in enumerate(program.rungs, start=1):
        label_part = f" | {rung.label}" if rung.label else ""
        lines.append(f"(* --- Rung {i}, step {rung.step}{label_part} --- *)")
        if not rung.actions:
            lines.append(f"(* condition: {rung.condition.to_st()} *)")
            lines.append("")
            continue
        for action in rung.actions:
            lines.extend(_emit_action(action))
        lines.append("")

    if program.unsupported:
        lines.append("(* --- Unsupported / review --- *)")
        for item in program.unsupported:
            lines.append(f"(* {item} *)")
        lines.append("")
    return lines


def generate_st_parts(program: ProgramIR, context: dict, *, pou_name: str | None = None) -> tuple[str, str]:
    """Return (declaration, implementation) for CODESYS two-pane paste."""
    signature_name = pou_name or program.name
    pulse_vars = _collect_pulse_vars(program)
    decl_lines = [f"PROGRAM {signature_name}"]
    decl_lines.extend(
        _emit_var_block(
            context.get("var_hints", []),
            context.get("device_comments", {}),
            pulse_vars,
        )
    )
    return "\n".join(decl_lines), "\n".join(_emit_implementation(program))


def generate_st(program: ProgramIR, context: dict, *, target: str = "codesys", pou_name: str | None = None) -> str:
    """Generate ST text. target='codesys' uses Declaration/Implementation sections."""
    signature_name = pou_name or program.name
    pulse_vars = _collect_pulse_vars(program)
    header = [
        f"(* Generated ST from context: {program.name} *)",
        f"(* Project: {program.project} *)",
        f"(* CPU: {program.cpu} *)",
    ]

    if target == "codesys":
        declaration, implementation = generate_st_parts(program, context, pou_name=pou_name)
        lines = header + [
            "",
            "(* ============================================================ *)",
            "(* [STEP 1] CODESYS > POU 열기 > DECLARATION(선언) 탭 > 아래만 붙여넣기 *)",
            f"(*          POU 이름과 PROGRAM 이름이 같아야 함: '{signature_name}' *)",
            "(* ============================================================ *)",
            "",
            declaration,
            "",
            "(* ============================================================ *)",
            "(* [STEP 2] CODESYS > 같은 POU > IMPLEMENTATION(구현) 탭 > 아래만 붙여넣기 *)",
            "(*          VAR 블록은 여기 넣으면 안 됨 *)",
            "(* ============================================================ *)",
            "",
            implementation,
            "",
        ]
        return "\n".join(lines)

    lines = header + ["", f"PROGRAM {signature_name}"]
    lines.extend(
        _emit_var_block(
            context.get("var_hints", []),
            context.get("device_comments", {}),
            pulse_vars,
        )
    )
    lines.append("")
    lines.extend(_emit_implementation(program))
    lines.append("END_PROGRAM")
    lines.append("")
    return "\n".join(lines)
