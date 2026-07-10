from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ..ladder_layout import (
    _match_anb_or_block,
    _match_and_or_tail,
    _match_gripper_orb_prefix,
    _match_or_and_tail,
    _match_series_or_tail,
    _match_triple_rail_orb,
)
from ..models import ActionKind, BoolExpr, Rung
from ..st_parser import parse_st_file

_CATALOG_PATH = Path(__file__).with_name("catalog.json")


@dataclass(frozen=True)
class PatternSpec:
    id: str
    name: str
    bool_shape: str
    topology: str
    layout_handler: str
    pdf_examples: list[dict[str, Any]]
    notes: str


def load_catalog() -> dict[str, Any]:
    return json.loads(_CATALOG_PATH.read_text(encoding="utf-8"))


def load_patterns() -> list[PatternSpec]:
    data = load_catalog()
    return [
        PatternSpec(
            id=p["id"],
            name=p["name"],
            bool_shape=p["bool_shape"],
            topology=p["topology"],
            layout_handler=p["layout_handler"],
            pdf_examples=p.get("pdf_examples", []),
            notes=p.get("notes", ""),
        )
        for p in data["patterns"]
    ]


def get_pattern(pattern_id: str) -> PatternSpec | None:
    for pattern in load_patterns():
        if pattern.id == pattern_id:
            return pattern
    return None


def get_style() -> dict[str, Any]:
    return load_catalog()["style"]


def _is_contact_series(expr: BoolExpr) -> bool:
    if expr.op == "CONTACT":
        return True
    if expr.op == "NOT" and expr.args and expr.args[0].op == "CONTACT":
        return True
    if expr.op == "AND":
        return all(_is_contact_series(arg) for arg in expr.args)
    return False


def classify_condition(expr: BoolExpr) -> str:
    if _match_triple_rail_orb(expr):
        return "triple_rail_orb_timer"
    if _match_gripper_orb_prefix(expr):
        return "gripper_orb"
    if _match_anb_or_block(expr):
        return "head_fork_or"
    if _match_and_or_tail(expr):
        return "and_or_tail"
    if _match_or_and_tail(expr):
        return "or_and_tail"
    if _match_series_or_tail(expr):
        return "nested_or_in_and"
    if expr.op == "OR" and len(expr.args) >= 2:
        if all(_is_contact_series(arg) for arg in expr.args):
            return "parallel_or"
    if expr.op == "AND" and _is_contact_series(expr):
        return "series_and"
    return "generic"



def effective_condition(rung: Rung) -> BoolExpr:
    for action in rung.actions:
        if action.condition and action.condition.op != "TRUE":
            return action.condition
    return rung.condition


def classify_rung(rung: Rung) -> str:
    pattern = classify_condition(effective_condition(rung))
    if pattern != "generic":
        return pattern

    if len(rung.actions) > 1:
        return "parallel_outputs"
    if rung.actions and rung.actions[0].kind in {ActionKind.SET, ActionKind.RST}:
        return "set_rst"
    if rung.actions and rung.actions[0].kind == ActionKind.TON_COIL:
        return "timer_on_branch"

    if any(a.kind == ActionKind.TON_COIL for a in rung.actions):
        return "timer_on_branch"
    return "generic"


def scan_program(st_path: str | Path) -> list[dict[str, Any]]:
    program = parse_st_file(st_path)
    rows: list[dict[str, Any]] = []
    for index, rung in enumerate(program.rungs, start=1):
        pattern_id = classify_rung(rung)
        pattern = get_pattern(pattern_id)
        rows.append(
            {
                "program": program.name,
                "rung": index,
                "step": rung.step,
                "label": rung.label,
                "pattern_id": pattern_id,
                "pattern_name": pattern.name if pattern else "unclassified",
                "layout_handler": pattern.layout_handler if pattern else "",
                "condition": rung.condition.to_st()[:120],
            }
        )
    return rows


def scan_all(st_dir: str | Path) -> dict[str, list[dict[str, Any]]]:
    st_dir = Path(st_dir)
    return {
        path.stem: scan_program(path)
        for path in sorted(st_dir.glob("P*.st"))
    }


def print_scan_report(st_dir: str | Path) -> None:
    report = scan_all(st_dir)
    counts: dict[str, int] = {}
    for program, rows in report.items():
        print(f"\n== {program} ==")
        for row in rows:
            counts[row["pattern_id"]] = counts.get(row["pattern_id"], 0) + 1
            step = row["step"] if row["step"] is not None else "-"
            print(
                f"  R{row['rung']:>2} step {step:>4}  "
                f"[{row['pattern_id']}] {row['pattern_name']}"
            )
    print("\n== pattern usage (all programs) ==")
    for pattern_id, count in sorted(counts.items(), key=lambda x: (-x[1], x[0])):
        pattern = get_pattern(pattern_id)
        name = pattern.name if pattern else pattern_id
        print(f"  {pattern_id:24} {count:3}  {name}")


def main() -> None:
    import argparse

    from ..paths import ST_DIR

    parser = argparse.ArgumentParser(description="Ladder pattern catalog and ST rung scanner")
    parser.add_argument("--list", action="store_true", help="list pattern catalog")
    parser.add_argument("--scan", action="store_true", help="classify rungs in ST files")
    parser.add_argument("--st-dir", default=str(ST_DIR), help="ST directory for --scan")
    args = parser.parse_args()

    if args.list:
        style = get_style()
        print("Style:", json.dumps(style, ensure_ascii=False, indent=2))
        print()
        for pattern in load_patterns():
            print(f"- {pattern.id}: {pattern.name}")
            print(f"  shape: {pattern.bool_shape}")
            print(f"  handler: {pattern.layout_handler}")
            if pattern.pdf_examples:
                ex = pattern.pdf_examples[0]
                print(f"  example: {ex.get('program')} rung {ex.get('rung')} step {ex.get('step')}")
            print()
        return

    if args.scan:
        print_scan_report(args.st_dir)
        return

    parser.print_help()


if __name__ == "__main__":
    main()
