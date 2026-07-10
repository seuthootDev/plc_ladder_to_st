from __future__ import annotations

from dataclasses import dataclass, field

from .models import ActionKind, BoolExpr, ProgramIR, Rung, RungAction, st_name

CONTACT_W = 56
CONTACT_H = 26
COIL_W = 80
COIL_H = 26
TIMER_W = 100
TIMER_H = 36
MOV_W = 110
MOV_H = 32
CONTACT_GAP = 6
BRANCH_GAP = 16
FORK_W = 12
FORK_STUB = 6
RUNG_PAD_Y = 14
LEFT_RAIL = 24
LABEL_W = 180
ACTION_GAP = 10
COIL_GAP = 24
MIN_COIL_X = LEFT_RAIL + LABEL_W + 160
COND_ORIGIN = LEFT_RAIL + LABEL_W


def _at_rung_origin(x: float) -> bool:
    return x <= COND_ORIGIN + 2


def _rail_from_left(main_y: float, x: float) -> Drawable | None:
    """Left power rail stub only at the rung condition origin (not nested forks)."""
    if _at_rung_origin(x):
        return _wire_h(LEFT_RAIL, main_y, x)
    return None

SYMBOL_KINDS = frozenset(
    {
        "contact_no",
        "contact_nc",
        "contact_pls",
        "contact_ne",
        "coil",
        "coil_set",
        "coil_rst",
        "timer",
        "mov",
        "unknown",
    }
)


@dataclass
class Drawable:
    kind: str
    x: float
    y: float
    w: float = 0
    h: float = 0
    x2: float = 0
    y2: float = 0
    text: str = ""
    subtext: str = ""


@dataclass
class RungLayout:
    rung_no: int
    step: int | None
    label: str
    y: float
    height: float
    drawables: list[Drawable] = field(default_factory=list)


@dataclass
class LadderLayout:
    width: float
    height: float
    rungs: list[RungLayout] = field(default_factory=list)


@dataclass
class _Size:
    width: float
    height: float
    merge_x: float | None = None
    merge_y: float | None = None


def _expr_has_or(expr: BoolExpr) -> bool:
    if expr.op == "OR":
        return True
    return any(_expr_has_or(arg) for arg in expr.args)


def _wire_h(x1: float, y: float, x2: float) -> Drawable | None:
    if x2 - x1 < 1:
        return None
    return Drawable(kind="wire_h", x=x1, y=y, x2=x2, y2=y)


def _wire_v(x: float, y1: float, y2: float) -> Drawable | None:
    if abs(y2 - y1) < 1:
        return None
    return Drawable(kind="wire_v", x=x, y=y1, x2=x, y2=y2)


def _symbol_bounds(items: list[Drawable]) -> tuple[float, float, float, float] | None:
    symbols = [d for d in items if d.kind in SYMBOL_KINDS]
    if not symbols:
        return None
    return (
        min(d.x for d in symbols),
        min(d.y for d in symbols),
        max(d.x + d.w for d in symbols),
        max(d.y + d.h for d in symbols),
    )


def _is_simple_series(expr: BoolExpr) -> bool:
    if expr.op in {"CONTACT", "CMP_NE"}:
        return True
    if expr.op == "NOT" and expr.args:
        return _is_simple_series(expr.args[0])
    return False


def _is_contact_series(expr: BoolExpr) -> bool:
    if expr.op in {"CONTACT", "CMP_NE"}:
        return True
    if expr.op == "NOT" and expr.args:
        return _is_contact_series(expr.args[0])
    if expr.op == "AND":
        return all(_is_contact_series(arg) for arg in expr.args)
    return False


def _match_and_or_tail(expr: BoolExpr) -> tuple[BoolExpr, BoolExpr, list[BoolExpr]] | None:
    """M215--+--(M1552-T70)--+--X103C...  OR block in the middle of an AND chain."""
    parts = _flatten_and(expr)
    or_idx = next((i for i, part in enumerate(parts) if part.op == "OR"), None)
    if or_idx is None or or_idx < 1:
        return None
    head = parts[0]
    if not _is_contact_series(head):
        return None
    or_block = parts[or_idx]
    if or_block.op != "OR" or len(or_block.args) < 2:
        return None
    if not all(_is_contact_series(branch) for branch in or_block.args):
        return None
    return head, or_block, parts[or_idx + 1 :]


def _layout_and_or_tail(
    head: BoolExpr,
    or_block: BoolExpr,
    tail: list[BoolExpr],
    x: float,
    y: float,
) -> tuple[_Size, list[Drawable]]:
    """Head, forked OR branches, then tail contacts continue on the main row."""
    items: list[Drawable] = []
    main_y = y + CONTACT_H / 2

    _, head_items = _layout_expr(head, x, y)
    items.extend(head_items)
    head_bounds = _symbol_bounds(head_items)
    head_right = head_bounds[2] if head_bounds else x + CONTACT_W
    fork_x = head_right + FORK_W

    branch_rows: list[tuple[float, float, float]] = []
    tier_bottom = y
    for i, branch in enumerate(or_block.args):
        branch_y = y if i == 0 else tier_bottom + BRANCH_GAP
        branch_start = fork_x + FORK_STUB
        bsize, branch_items = _layout_expr(branch, branch_start, branch_y)
        items.extend(branch_items)
        bounds = _symbol_bounds(branch_items)
        mid_y = bsize.merge_y if bsize.merge_y is not None else branch_y + CONTACT_H / 2
        entry = bounds[0] if bounds else branch_start
        right = bsize.merge_x if bsize.merge_x is not None else (bounds[2] if bounds else branch_start)
        branch_rows.append((mid_y, entry, right))
        tier_bottom = max(tier_bottom, branch_y + bsize.height)

    or_merge_x = max([head_right, *(right for _, _, right in branch_rows)])

    rail_main = _rail_from_left(main_y, x)
    if rail_main:
        items.append(rail_main)
    head_stub = _wire_h(head_right, main_y, fork_x)
    if head_stub:
        items.append(head_stub)
    if len(branch_rows) > 1:
        fork_bus = _wire_v(fork_x, branch_rows[0][0], branch_rows[-1][0])
        if fork_bus:
            items.append(fork_bus)
    for mid_y, entry, right in branch_rows:
        entry_wire = _wire_h(fork_x, mid_y, entry)
        if entry_wire:
            items.append(entry_wire)
        if right < or_merge_x - 1:
            stub = _wire_h(right, mid_y, or_merge_x)
            if stub:
                items.append(stub)
        if mid_y != main_y:
            join = _wire_v(or_merge_x, mid_y, main_y)
            if join:
                items.append(join)
    if branch_rows and branch_rows[0][2] < or_merge_x - 1:
        ext = _wire_h(branch_rows[0][2], main_y, or_merge_x)
        if ext:
            items.append(ext)

    end_x = or_merge_x
    if tail:
        tail_start = or_merge_x + FORK_STUB
        tail_expr = tail[0] if len(tail) == 1 else BoolExpr(op="AND", args=list(tail))
        _, tail_items = _layout_contact_series(tail_expr, tail_start, y)
        items.extend(tail_items)
        tail_bounds = _symbol_bounds(tail_items)
        if tail_bounds:
            tail_entry = tail_bounds[0]
            tail_wire = _wire_h(or_merge_x, main_y, tail_entry)
            if tail_wire:
                items.append(tail_wire)
            end_x = tail_bounds[2]

    if branch_rows:
        total_h = max(CONTACT_H, tier_bottom - y)
    else:
        total_h = CONTACT_H
    if tail:
        total_h = max(total_h, y + CONTACT_H - y)

    return _Size(end_x - x, total_h, merge_x=end_x, merge_y=main_y), items


def _match_or_and_tail(expr: BoolExpr) -> tuple[BoolExpr, list[BoolExpr]] | None:
    """(A OR B) AND tail...  e.g. step 92 (Y100A|Y100C) AND /M2005..."""
    parts = _flatten_and(expr)
    if not parts or parts[0].op != "OR":
        return None
    or_block = parts[0]
    if len(or_block.args) < 2:
        return None
    if not all(_is_contact_series(branch) for branch in or_block.args):
        return None
    tail = parts[1:]
    if not tail:
        return None
    return or_block, tail


def _layout_or_and_tail(
    or_block: BoolExpr,
    tail: list[BoolExpr],
    x: float,
    y: float,
) -> tuple[_Size, list[Drawable]]:
    """OR block on the main row, then tail contacts continue horizontally."""
    items: list[Drawable] = []
    osize, opart = _layout_expr(or_block, x, y)
    items.extend(opart)

    main_y = osize.merge_y if osize.merge_y is not None else y + CONTACT_H / 2
    merge_x = osize.merge_x
    if merge_x is None:
        obounds = _symbol_bounds(opart)
        merge_x = obounds[2] if obounds else x + CONTACT_W

    end_x = merge_x
    max_h = osize.height

    if tail:
        tail_start = merge_x + FORK_STUB
        tail_expr = tail[0] if len(tail) == 1 else BoolExpr(op="AND", args=list(tail))
        _, tail_items = _layout_contact_series(tail_expr, tail_start, y)
        items.extend(tail_items)
        tbounds = _symbol_bounds(tail_items)
        if tbounds:
            tail_wire = _wire_h(merge_x, main_y, tbounds[0])
            if tail_wire:
                items.append(tail_wire)
            end_x = tbounds[2]
        max_h = max(max_h, CONTACT_H)

    return _Size(end_x - x, max_h, merge_x=end_x, merge_y=main_y), items


def _match_series_or_tail(
    expr: BoolExpr,
) -> tuple[list[BoolExpr], BoolExpr, list[BoolExpr]] | None:
    """prefix on main row, OR branches fork/merge, tail continues on main row."""
    parts = _flatten_and(expr)
    or_idx = next((i for i, part in enumerate(parts) if part.op == "OR"), None)
    if or_idx is None or or_idx < 1:
        return None
    or_block = parts[or_idx]
    if or_block.op != "OR" or len(or_block.args) < 2:
        return None
    return parts[:or_idx], or_block, parts[or_idx + 1 :]


def _layout_series_or_tail(
    prefix: list[BoolExpr],
    or_block: BoolExpr,
    tail: list[BoolExpr],
    x: float,
    y: float,
) -> tuple[_Size, list[Drawable]]:
    """Main-line prefix, forked OR (merge back), then tail on main row."""
    items: list[Drawable] = []
    main_y = y + CONTACT_H / 2

    rail = _rail_from_left(main_y, x)
    if rail:
        items.append(rail)

    prefix_expr = prefix[0] if len(prefix) == 1 else BoolExpr(op="AND", args=list(prefix))
    _, prefix_items = _layout_contact_series(prefix_expr, x, y)
    items.extend(prefix_items)
    pbounds = _symbol_bounds(prefix_items)
    prefix_end = pbounds[2] if pbounds else x + CONTACT_W

    fork_x = prefix_end + FORK_W
    to_fork = _wire_h(prefix_end, main_y, fork_x)
    if to_fork:
        items.append(to_fork)

    merge_x, or_items, block_h = _layout_or_at_fork(or_block, fork_x, y, main_y)
    items.extend(or_items)

    end_x = merge_x
    max_h = max(CONTACT_H, block_h)

    if tail:
        tail_start = merge_x + FORK_STUB
        tail_expr = tail[0] if len(tail) == 1 else BoolExpr(op="AND", args=list(tail))
        tsize, tail_items = _layout_expr(tail_expr, tail_start, y)
        items.extend(tail_items)
        tbounds = _symbol_bounds(tail_items)
        if tbounds:
            tail_wire = _wire_h(merge_x, main_y, tbounds[0])
            if tail_wire:
                items.append(tail_wire)
            end_x = tbounds[2]
        max_h = max(max_h, tsize.height)

    return _Size(end_x - x, max_h, merge_x=end_x, merge_y=main_y), items


def _layout_or_at_fork(
    or_block: BoolExpr,
    fork_x: float,
    y: float,
    main_y: float,
) -> tuple[float, list[Drawable], float]:
    """OR branches from an in-line fork; each tier stacks below the previous block height."""
    items: list[Drawable] = []
    branch_rows: list[tuple[float, float, float]] = []
    tier_bottom = y

    for i, branch in enumerate(or_block.args):
        branch_y = y if i == 0 else tier_bottom + BRANCH_GAP
        branch_start = fork_x + FORK_STUB
        bsize, branch_items = _layout_expr(branch, branch_start, branch_y)
        items.extend(branch_items)
        bounds = _symbol_bounds(branch_items)
        mid_y = bsize.merge_y if bsize.merge_y is not None else branch_y + CONTACT_H / 2
        entry = bounds[0] if bounds else branch_start
        right = bsize.merge_x if bsize.merge_x is not None else (bounds[2] if bounds else branch_start)
        branch_rows.append((mid_y, entry, right))
        tier_bottom = max(tier_bottom, branch_y + bsize.height)

    merge_x = max(right for _, _, right in branch_rows)

    if len(branch_rows) > 1:
        fork_bus = _wire_v(fork_x, branch_rows[0][0], branch_rows[-1][0])
        if fork_bus:
            items.append(fork_bus)

    for mid_y, entry, right in branch_rows:
        entry_wire = _wire_h(fork_x, mid_y, entry)
        if entry_wire:
            items.append(entry_wire)
        if right < merge_x - 1:
            stub = _wire_h(right, mid_y, merge_x)
            if stub:
                items.append(stub)
        if mid_y != main_y:
            join = _wire_v(merge_x, mid_y, main_y)
            if join:
                items.append(join)

    if branch_rows and branch_rows[0][2] < merge_x - 1:
        ext = _wire_h(branch_rows[0][2], main_y, merge_x)
        if ext:
            items.append(ext)

    block_h = max(CONTACT_H, tier_bottom - y)
    return merge_x, items, block_h


def _use_rung_or_fork(expr: BoolExpr) -> bool:
    """ORB-style OR: first path from rail, later paths fork from first merge."""
    if expr.op != "OR" or len(expr.args) < 2:
        return False
    if _is_contact_series(expr.args[0]) and all(_is_contact_series(a) for a in expr.args):
        return False
    return not _is_contact_series(expr.args[0])


def _layout_rung_origin_or_fork(expr: BoolExpr, x: float, y: float) -> tuple[_Size, list[Drawable]]:
    """Layout arg0 from left rail; remaining OR args branch from arg0 merge."""
    items: list[Drawable] = []
    size0, part0 = _layout_expr(expr.args[0], x, y)
    items.extend(part0)

    main_y = size0.merge_y if size0.merge_y is not None else y + CONTACT_H / 2
    merge_x = size0.merge_x
    if merge_x is None:
        bounds0 = _symbol_bounds(part0)
        merge_x = bounds0[2] if bounds0 else x + CONTACT_W

    fork_x = merge_x + FORK_W
    to_fork = _wire_h(merge_x, main_y, fork_x)
    if to_fork:
        items.append(to_fork)

    tier_bottom = y + size0.height
    branch_rights: list[tuple[float, float]] = [(main_y, merge_x)]

    for arg in expr.args[1:]:
        path_y = tier_bottom + BRANCH_GAP
        path_mid = path_y + CONTACT_H / 2
        branch_start = fork_x + FORK_STUB
        bsize, bpart = _layout_expr(arg, branch_start, path_y)
        items.extend(bpart)
        if bsize.merge_y is not None:
            path_mid = bsize.merge_y
        bbounds = _symbol_bounds(bpart)
        if bsize.merge_x is not None:
            bright = bsize.merge_x
        elif bbounds:
            bright = bbounds[2]
        else:
            bright = branch_start + CONTACT_W
        if bbounds:
            entry = _wire_h(fork_x, path_mid, bbounds[0])
            if entry:
                items.append(entry)
        branch_rights.append((path_mid, bright))
        tier_bottom = max(tier_bottom, path_y + bsize.height)

    final_merge = max(right for _, right in branch_rights)
    if len(branch_rights) > 1:
        fork_bus = _wire_v(fork_x, branch_rights[0][0], branch_rights[-1][0])
        if fork_bus:
            items.append(fork_bus)

    for path_mid, right in branch_rights[1:]:
        if right < final_merge - 1:
            stub = _wire_h(right, path_mid, final_merge)
            if stub:
                items.append(stub)
        if path_mid != main_y:
            join = _wire_v(final_merge, path_mid, main_y)
            if join:
                items.append(join)

    if branch_rights[0][1] < final_merge - 1:
        ext = _wire_h(branch_rights[0][1], main_y, final_merge)
        if ext:
            items.append(ext)

    total_h = tier_bottom - y
    return _Size(final_merge - x, total_h, merge_x=final_merge, merge_y=main_y), items


def _match_triple_rail_orb(expr: BoolExpr) -> tuple[BoolExpr, BoolExpr, BoolExpr] | None:
    """OR( (branchA | branchB) & Tn , altSeries ) — 3 rails merge at Tn (P99 step 41/65)."""
    if expr.op != "OR" or len(expr.args) != 2:
        return None
    left, right = expr.args
    if not _is_contact_series(right):
        return None
    parts = _flatten_and(left)
    if len(parts) != 2:
        return None
    or_block, timer = parts[0], parts[1]
    if or_block.op != "OR" or len(or_block.args) != 2:
        return None
    if not all(_is_contact_series(b) for b in or_block.args):
        return None
    if not (timer.op == "CONTACT" and timer.device.upper().startswith("T")):
        return None
    return or_block, timer, right


def _layout_triple_rail_orb(
    or_block: BoolExpr,
    timer: BoolExpr,
    alt_path: BoolExpr,
    x: float,
    y: float,
) -> tuple[_Size, list[Drawable]]:
    """3 lines from left rail; inner OR + Tn on rows 0–1; row 2 joins after Tn."""
    items: list[Drawable] = []
    row_gap = CONTACT_H + BRANCH_GAP
    y0 = y
    y1 = y + row_gap
    y2 = y + 2 * row_gap
    mid0 = y0 + CONTACT_H / 2
    mid1 = y1 + CONTACT_H / 2
    mid2 = y2 + CONTACT_H / 2

    rail = _rail_from_left(mid0, x)
    if rail:
        items.append(rail)
    if mid2 != mid0:
        left_bus = _wire_v(LEFT_RAIL, mid0, mid2)
        if left_bus:
            items.append(left_bus)

    rows = [
        (y0, mid0, or_block.args[0]),
        (y1, mid1, or_block.args[1]),
        (y2, mid2, alt_path),
    ]
    ends: list[float] = []
    for path_y, path_mid, branch in rows:
        _, branch_items = _layout_contact_series(branch, x, path_y)
        items.extend(branch_items)
        bounds = _symbol_bounds(branch_items)
        ends.append(bounds[2] if bounds else x + CONTACT_W)
        if bounds:
            entry = _wire_h(LEFT_RAIL, path_mid, bounds[0])
            if entry:
                items.append(entry)

    inner_merge_x = max(ends[0], ends[1]) + FORK_W
    inner_bus = _wire_v(inner_merge_x, mid0, mid1)
    if inner_bus:
        items.append(inner_bus)
    for end_x, path_mid in ((ends[0], mid0), (ends[1], mid1)):
        stub = _wire_h(end_x, path_mid, inner_merge_x)
        if stub:
            items.append(stub)

    t_x = inner_merge_x + FORK_STUB
    tsize, titems = _layout_expr(timer, t_x, y0)
    items.extend(titems)
    tbounds = _symbol_bounds(titems)
    t_end = tsize.merge_x if tsize.merge_x is not None else (tbounds[2] if tbounds else t_x + CONTACT_W)
    if tbounds:
        to_t = _wire_h(inner_merge_x, mid0, tbounds[0])
        if to_t:
            items.append(to_t)

    junction_x = t_end + FORK_W
    if ends[2] < junction_x - 1:
        alt_stub = _wire_h(ends[2], mid2, junction_x)
        if alt_stub:
            items.append(alt_stub)
    join_bus = _wire_v(junction_x, mid0, mid2)
    if join_bus:
        items.append(join_bus)
    to_junction = _wire_h(t_end, mid0, junction_x)
    if to_junction:
        items.append(to_junction)

    total_h = y2 + CONTACT_H - y
    return _Size(junction_x - x, total_h, merge_x=junction_x, merge_y=mid0), items, ends[2], mid2


def _layout_triple_rail_parallel_rung(
    condition: BoolExpr,
    actions: list[RungAction],
    base_y: float,
    coil_x: float,
) -> tuple[float, list[Drawable]]:
    """Triple-rail ORB: M coil from junction; timer coil continues on M2100/M212 row."""
    triple = _match_triple_rail_orb(condition)
    if not triple:
        return _layout_parallel_actions(condition, actions, base_y, coil_x)

    or_block, timer_contact, alt_path = triple
    wires: list[Drawable] = []
    symbols: list[Drawable] = []
    cond_origin = LEFT_RAIL + LABEL_W

    csize, cond_items, alt_end_x, alt_mid_y = _layout_triple_rail_orb(
        or_block, timer_contact, alt_path, cond_origin, base_y
    )
    symbols.extend(cond_items)

    junction_x = csize.merge_x if csize.merge_x is not None else cond_origin + CONTACT_W
    main_mid = csize.merge_y if csize.merge_y is not None else base_y + CONTACT_H / 2
    alt_y = base_y + 2 * (CONTACT_H + BRANCH_GAP)

    coil_act = next(a for a in actions if a.kind != ActionKind.TON_COIL)
    timer_act = next(a for a in actions if a.kind == ActionKind.TON_COIL)

    coil_size, coil_items = _layout_action(coil_act, coil_x, base_y)
    symbols.extend(coil_items)
    to_coil = _wire_h(junction_x, main_mid, coil_x)
    if to_coil:
        wires.append(to_coil)
    coil_tail = _wire_h(coil_x + coil_size.width, main_mid, coil_x + coil_size.width + 20)
    if coil_tail:
        wires.append(coil_tail)

    timer_size, timer_items = _layout_action(timer_act, coil_x, alt_y)
    symbols.extend(timer_items)
    to_timer = _wire_h(alt_end_x, alt_mid_y, coil_x)
    if to_timer:
        wires.append(to_timer)
    timer_tail = _wire_h(coil_x + timer_size.width, alt_mid_y, coil_x + timer_size.width + 20)
    if timer_tail:
        wires.append(timer_tail)

    total_h = max(csize.height, alt_y + timer_size.height - base_y)
    return total_h, wires + symbols


def _match_gripper_orb_prefix(
    expr: BoolExpr,
) -> tuple[list[BoolExpr], BoolExpr, BoolExpr] | None:
    """OR( AND(prefix, innerOR), altSeries ) — P99 step 83 (Y54/Y56/X1C|X1D | M3100/M212)."""
    if expr.op != "OR" or len(expr.args) != 2:
        return None
    main, alt = expr.args
    if not _is_contact_series(alt):
        return None
    main_parts = _flatten_and(main)
    if len(main_parts) < 2:
        return None
    inner_or = main_parts[-1]
    if inner_or.op != "OR" or len(inner_or.args) != 2:
        return None
    if not all(_is_simple_series(arg) for arg in inner_or.args):
        return None
    prefix_parts = main_parts[:-1]
    if not prefix_parts or not all(_is_contact_series(part) for part in prefix_parts):
        return None
    return prefix_parts, inner_or, alt


def _layout_gripper_orb(
    prefix_parts: list[BoolExpr],
    inner_or: BoolExpr,
    alt_path: BoolExpr,
    timer: BoolExpr | None,
    x: float,
    y: float,
) -> tuple[_Size, list[Drawable], float, float]:
    """3 rails: row0 /X1C+Tn; row1 X1D; row2 M3100/M212 merges at ORB junction."""
    items: list[Drawable] = []
    row_gap = CONTACT_H + BRANCH_GAP
    y0 = y
    y1 = y + row_gap
    y2 = y + 2 * row_gap
    mid0 = y0 + CONTACT_H / 2
    mid1 = y1 + CONTACT_H / 2
    mid2 = y2 + CONTACT_H / 2

    prefix_expr = (
        prefix_parts[0]
        if len(prefix_parts) == 1
        else BoolExpr(op="AND", args=list(prefix_parts))
    )
    _, prefix_items = _layout_contact_series(prefix_expr, x, y0)
    items.extend(prefix_items)
    pbounds = _symbol_bounds(prefix_items)
    prefix_end = pbounds[2] if pbounds else x + CONTACT_W
    fork_x = prefix_end + FORK_W

    rail = _rail_from_left(mid0, x)
    if rail:
        items.append(rail)
    left_bus = _wire_v(LEFT_RAIL, mid0, mid2)
    if left_bus:
        items.append(left_bus)

    to_fork = _wire_h(prefix_end, mid0, fork_x)
    if to_fork:
        items.append(to_fork)
    fork_bus = _wire_v(fork_x, mid0, mid1)
    if fork_bus:
        items.append(fork_bus)

    branch_x = fork_x + FORK_STUB
    row0_branch = inner_or.args[0]
    if timer is not None:
        row0_branch = BoolExpr(op="AND", args=[inner_or.args[0], timer])
    _, x1c_items = _layout_contact_series(row0_branch, branch_x, y0)
    items.extend(x1c_items)
    x1c_bounds = _symbol_bounds(x1c_items)
    x1c_path_end = x1c_bounds[2] if x1c_bounds else branch_x + CONTACT_W
    x1c_entry = _wire_h(fork_x, mid0, branch_x)
    if x1c_entry:
        items.append(x1c_entry)

    _, x1d_items = _layout_contact_series(inner_or.args[1], branch_x, y1)
    items.extend(x1d_items)
    x1d_bounds = _symbol_bounds(x1d_items)
    x1d_end = x1d_bounds[2] if x1d_bounds else branch_x + CONTACT_W
    x1d_entry = _wire_h(fork_x, mid1, branch_x)
    if x1d_entry:
        items.append(x1d_entry)

    inner_merge_x = max(x1c_path_end, x1d_end)
    if x1c_path_end < inner_merge_x - 1:
        x1c_stub = _wire_h(x1c_path_end, mid0, inner_merge_x)
        if x1c_stub:
            items.append(x1c_stub)
    inner_join = _wire_v(inner_merge_x, mid1, mid0)
    if inner_join:
        items.append(inner_join)

    _, alt_items = _layout_contact_series(alt_path, x, y2)
    items.extend(alt_items)
    alt_bounds = _symbol_bounds(alt_items)
    alt_end = alt_bounds[2] if alt_bounds else x + CONTACT_W
    if alt_bounds:
        alt_entry = _wire_h(LEFT_RAIL, mid2, alt_bounds[0])
        if alt_entry:
            items.append(alt_entry)

    junction_x = max(inner_merge_x, alt_end)
    if alt_end < junction_x - 1:
        alt_stub = _wire_h(alt_end, mid2, junction_x)
        if alt_stub:
            items.append(alt_stub)
    outer_join = _wire_v(junction_x, mid2, mid0)
    if outer_join:
        items.append(outer_join)
    if inner_merge_x < junction_x - 1:
        inner_ext = _wire_h(inner_merge_x, mid0, junction_x)
        if inner_ext:
            items.append(inner_ext)

    total_h = y2 + CONTACT_H - y
    return _Size(junction_x - x, total_h, merge_x=junction_x, merge_y=mid0), items, x1d_end, mid1


def _can_gripper_orb(actions: list[RungAction], rung: Rung) -> bool:
    if len(actions) != 2:
        return False
    conditions = [_action_condition(action, rung) for action in actions]
    prefix, suffixes = _extract_common_and_prefix(conditions)
    if _match_gripper_orb_prefix(prefix) is None:
        return False
    has_timer_contact = any(
        suffix.op == "CONTACT" and suffix.device.upper().startswith("T") for suffix in suffixes
    )
    has_true = any(suffix.op == "TRUE" for suffix in suffixes)
    has_coil = any(action.kind == ActionKind.OUT for action in actions)
    has_ton = any(action.kind == ActionKind.TON_COIL for action in actions)
    return has_timer_contact and has_true and has_coil and has_ton


def _layout_gripper_orb_rung(
    prefix: BoolExpr,
    actions: list[RungAction],
    suffixes: list[BoolExpr],
    base_y: float,
    coil_x: float,
) -> tuple[float, list[Drawable]]:
    """MPS/MPP gripper: M coil at ORB junction; timer coil continues on X1D→Tn row."""
    matched = _match_gripper_orb_prefix(prefix)
    if not matched:
        return _layout_shared_prefix_rung(prefix, actions, suffixes, base_y, coil_x)

    prefix_parts, inner_or, alt_path = matched
    wires: list[Drawable] = []
    symbols: list[Drawable] = []
    cond_origin = LEFT_RAIL + LABEL_W
    x1d_y = base_y + (CONTACT_H + BRANCH_GAP)

    timer_contact = next(
        suffix
        for suffix in suffixes
        if suffix.op == "CONTACT" and suffix.device.upper().startswith("T")
    )
    coil_action = next(
        action
        for suffix, action in zip(suffixes, actions)
        if suffix.op == "CONTACT" and suffix.device.upper().startswith("T")
    )
    timer_action = next(
        action for suffix, action in zip(suffixes, actions) if suffix.op == "TRUE"
    )

    csize, cond_items, x1d_end, x1d_mid_y = _layout_gripper_orb(
        prefix_parts, inner_or, alt_path, timer_contact, cond_origin, base_y
    )
    symbols.extend(cond_items)

    junction_x = csize.merge_x if csize.merge_x is not None else cond_origin + CONTACT_W
    main_mid = csize.merge_y if csize.merge_y is not None else base_y + CONTACT_H / 2

    coil_size, coil_items = _layout_action(coil_action, coil_x, base_y)
    symbols.extend(coil_items)
    to_coil = _wire_h(junction_x, main_mid, coil_x)
    if to_coil:
        wires.append(to_coil)
    coil_tail = _wire_h(coil_x + coil_size.width, main_mid, coil_x + coil_size.width + 20)
    if coil_tail:
        wires.append(coil_tail)

    timer_size, timer_items = _layout_action(timer_action, coil_x, x1d_y)
    symbols.extend(timer_items)
    to_timer = _wire_h(x1d_end, x1d_mid_y, coil_x)
    if to_timer:
        wires.append(to_timer)
    timer_tail = _wire_h(coil_x + timer_size.width, x1d_mid_y, coil_x + timer_size.width + 20)
    if timer_tail:
        wires.append(timer_tail)

    total_h = max(csize.height, x1d_y + timer_size.height - base_y)
    return total_h, wires + symbols


def _layout_flat_and_with_ors(expr: BoolExpr, x: float, y: float) -> tuple[_Size, list[Drawable]]:
    """Series contacts interleaved with OR blocks (e.g. step 98)."""
    parts = _flatten_and(expr)
    items: list[Drawable] = []
    main_y = y + CONTACT_H / 2
    exit_x = x
    max_h = CONTACT_H
    series_buf: list[BoolExpr] = []

    rail = _rail_from_left(main_y, x)
    if rail:
        items.append(rail)

    def flush_series() -> None:
        nonlocal exit_x, max_h, series_buf
        if not series_buf:
            return
        head = series_buf[0] if len(series_buf) == 1 else BoolExpr(op="AND", args=list(series_buf))
        _, part_items = _layout_contact_series(head, exit_x, y)
        items.extend(part_items)
        bounds = _symbol_bounds(part_items)
        if bounds:
            exit_x = bounds[2]
        series_buf = []

    for part in parts:
        if part.op == "OR":
            flush_series()
            fork_x = exit_x + FORK_W
            stub = _wire_h(exit_x, main_y, fork_x)
            if stub:
                items.append(stub)
            merge_x, or_items, block_h = _layout_or_at_fork(part, fork_x, y, main_y)
            items.extend(or_items)
            max_h = max(max_h, block_h)
            exit_x = merge_x
        else:
            series_buf.append(part)

    flush_series()
    return _Size(exit_x - x, max_h, merge_x=exit_x, merge_y=main_y), items


def _match_anb_or_block(expr: BoolExpr) -> tuple[BoolExpr, list[BoolExpr]] | None:
    """ANB + ORB stack: head AND (branch1 OR branch2 OR ...), no tail after OR."""
    if expr.op != "AND" or len(expr.args) != 2:
        return None
    head, inner = expr.args
    if not _is_contact_series(head):
        return None
    if inner.op != "OR":
        return None
    branches = inner.args
    if len(branches) < 2:
        return None
    if not all(_is_contact_series(branch) for branch in branches):
        return None
    return head, branches


def _layout_head_fork_or(
    head: BoolExpr,
    or_branches: list[BoolExpr],
    x: float,
    y: float,
) -> tuple[_Size, list[Drawable]]:
    """M202--+--(M211-SM412)  GX ANB/ORB: fork after head, not separate left-rail LD rows."""
    items: list[Drawable] = []
    main_y = y + CONTACT_H / 2

    _, head_items = _layout_expr(head, x, y)
    items.extend(head_items)
    head_bounds = _symbol_bounds(head_items)
    head_right = head_bounds[2] if head_bounds else x + CONTACT_W
    fork_x = head_right + FORK_W

    branch_rows: list[tuple[float, float, float]] = []
    tier_bottom = y

    for i, branch in enumerate(or_branches):
        branch_y = y if i == 0 else tier_bottom + BRANCH_GAP
        branch_start = fork_x + FORK_STUB
        bsize, branch_items = _layout_expr(branch, branch_start, branch_y)
        items.extend(branch_items)
        bounds = _symbol_bounds(branch_items)
        mid_y = bsize.merge_y if bsize.merge_y is not None else branch_y + CONTACT_H / 2
        entry = bounds[0] if bounds else branch_start
        right = bsize.merge_x if bsize.merge_x is not None else (bounds[2] if bounds else branch_start)
        branch_rows.append((mid_y, entry, right))
        tier_bottom = max(tier_bottom, branch_y + bsize.height)

    merge_x = max([head_right, *(right for _, _, right in branch_rows)])

    rail_main = _rail_from_left(main_y, x)
    if rail_main:
        items.append(rail_main)
    head_stub = _wire_h(head_right, main_y, fork_x)
    if head_stub:
        items.append(head_stub)

    if len(branch_rows) > 1:
        fork_bus = _wire_v(fork_x, branch_rows[0][0], branch_rows[-1][0])
        if fork_bus:
            items.append(fork_bus)

    for mid_y, entry, right in branch_rows:
        entry_wire = _wire_h(fork_x, mid_y, entry)
        if entry_wire:
            items.append(entry_wire)
        if right < merge_x - 1:
            stub = _wire_h(right, mid_y, merge_x)
            if stub:
                items.append(stub)
        if mid_y != main_y:
            join = _wire_v(merge_x, mid_y, main_y)
            if join:
                items.append(join)

    if branch_rows and branch_rows[0][2] < merge_x - 1:
        ext = _wire_h(branch_rows[0][2], main_y, merge_x)
        if ext:
            items.append(ext)

    total_h = max(CONTACT_H, tier_bottom - y) if branch_rows else CONTACT_H

    return _Size(merge_x - x, total_h, merge_x=merge_x, merge_y=main_y), items


def _layout_contact_series(expr: BoolExpr, x: float, y: float) -> tuple[_Size, list[Drawable]]:
    parts = _flatten_and(expr) if expr.op == "AND" else [expr]
    items: list[Drawable] = []
    cursor = x
    for i, part in enumerate(parts):
        size, part_items = _layout_expr(part, cursor, y)
        items.extend(part_items)
        cursor += size.width
        if i < len(parts) - 1:
            cursor += CONTACT_GAP
    width = max(0, cursor - x - (CONTACT_GAP if len(parts) > 1 else 0))
    bounds = _symbol_bounds(items)
    right = bounds[2] if bounds else x + width
    mid_y = y + CONTACT_H / 2
    return _Size(width, CONTACT_H, merge_x=right, merge_y=mid_y), items


def _condition_right_edge(cond_size: _Size, cond_items: list[Drawable], cond_origin: float) -> float:
    if cond_size.merge_x is not None:
        return cond_size.merge_x
    bounds = _symbol_bounds(cond_items)
    if bounds:
        return bounds[2]
    return cond_origin + cond_size.width


def _coil_x_for_condition(condition: BoolExpr, base_y: float) -> float:
    cond_origin = LEFT_RAIL + LABEL_W
    size, items = _layout_expr(condition, cond_origin, base_y)
    return max(MIN_COIL_X, _condition_right_edge(size, items, cond_origin) + COIL_GAP)


def _coil_x_for_rung(rung: Rung, base_y: float) -> float:
    actions = rung.actions or [RungAction(kind=ActionKind.OUT, target="?", condition=rung.condition)]

    if _can_parallel_actions(actions, rung):
        return _coil_x_for_condition(_action_condition(actions[0], rung), base_y)

    if _can_shared_prefix(actions, rung):
        conditions = [_action_condition(action, rung) for action in actions]
        prefix, suffixes = _extract_common_and_prefix(conditions)
        cond_origin = LEFT_RAIL + LABEL_W
        row_h = COIL_H
        main_y = base_y + row_h / 2
        _, prefix_items = _layout_expr(prefix, cond_origin, main_y - CONTACT_H / 2)
        pbounds = _symbol_bounds(prefix_items)
        prefix_right = pbounds[2] if pbounds else cond_origin
        fork_x = prefix_right + 12 + 8
        max_right = fork_x
        for suffix in suffixes:
            _, suffix_items = _layout_expr(suffix, fork_x, main_y - CONTACT_H / 2)
            sbounds = _symbol_bounds(suffix_items)
            if sbounds:
                max_right = max(max_right, sbounds[2])
        return max(MIN_COIL_X, max_right + COIL_GAP)

    coil_x = MIN_COIL_X
    for action in actions:
        cond = _action_condition(action, rung)
        coil_x = max(coil_x, _coil_x_for_condition(cond, base_y))
    return coil_x


def _drawables_right_edge(drawables: list[Drawable]) -> float:
    edge = 0.0
    for d in drawables:
        if d.kind == "label":
            continue
        if d.kind in SYMBOL_KINDS:
            edge = max(edge, d.x + d.w)
        elif d.kind in {"wire_h", "wire_v"}:
            edge = max(edge, d.x2, d.x)
    return edge


def _make_contact(device: str, x: float, y: float) -> Drawable:
    name = st_name(device)
    if name.endswith("_PLS"):
        return Drawable(
            kind="contact_pls",
            x=x,
            y=y,
            w=CONTACT_W,
            h=CONTACT_H,
            text=name[:-4],
        )
    return Drawable(kind="contact_no", x=x, y=y, w=CONTACT_W, h=CONTACT_H, text=name)


def _layout_expr(expr: BoolExpr, x: float, y: float) -> tuple[_Size, list[Drawable]]:
    if expr.op == "TRUE":
        return _Size(0, CONTACT_H), []

    if expr.op == "CONTACT":
        right = x + CONTACT_W
        mid_y = y + CONTACT_H / 2
        return _Size(CONTACT_W, CONTACT_H, merge_x=right, merge_y=mid_y), [
            _make_contact(expr.device, x, y)
        ]

    if expr.op == "NOT" and expr.args:
        inner_size, inner_items = _layout_expr(expr.args[0], x, y)
        device = ""
        for item in inner_items:
            if item.kind in {"contact_no", "contact_nc", "contact_pls"}:
                device = item.text
                item.kind = "contact_nc"
        if not device and expr.args[0].op == "CONTACT":
            device = st_name(expr.args[0].device)
            if device.endswith("_PLS"):
                device = device[:-4]
            return _Size(CONTACT_W, CONTACT_H, merge_x=x + CONTACT_W, merge_y=y + CONTACT_H / 2), [
                Drawable(kind="contact_nc", x=x, y=y, w=CONTACT_W, h=CONTACT_H, text=device)
            ]
        return inner_size, inner_items

    if expr.op == "AND":
        or_and = _match_or_and_tail(expr)
        if or_and:
            return _layout_or_and_tail(or_and[0], or_and[1], x, y)

        anb_or = _match_anb_or_block(expr)
        if anb_or:
            return _layout_head_fork_or(anb_or[0], anb_or[1], x, y)

        series_or = _match_series_or_tail(expr)
        if series_or:
            return _layout_series_or_tail(series_or[0], series_or[1], series_or[2], x, y)

        or_tail = _match_and_or_tail(expr)
        if or_tail:
            return _layout_and_or_tail(or_tail[0], or_tail[1], or_tail[2], x, y)

        flat_parts = _flatten_and(expr)
        if any(part.op == "OR" for part in flat_parts):
            return _layout_flat_and_with_ors(expr, x, y)

        items: list[Drawable] = []
        cursor = x
        max_h = CONTACT_H
        series_mid_y = y + CONTACT_H / 2
        prev_exit_x: float | None = None

        for i, arg in enumerate(expr.args):
            if i == 0:
                arg_y = y
            elif _is_simple_series(arg):
                arg_y = series_mid_y - CONTACT_H / 2
            else:
                arg_y = y

            size, part = _layout_expr(arg, cursor, arg_y)
            bounds = _symbol_bounds(part)
            items.extend(part)

            if size.merge_y is not None:
                series_mid_y = size.merge_y
            elif size.height <= CONTACT_H + 1:
                series_mid_y = arg_y + CONTACT_H / 2
            else:
                series_mid_y = arg_y + size.height / 2

            exit_x = size.merge_x
            if exit_x is None and bounds:
                exit_x = bounds[2]

            if bounds and prev_exit_x is not None:
                entry_x = bounds[0]
                wire = _wire_h(prev_exit_x, series_mid_y, entry_x)
                if wire:
                    items.append(wire)

            if exit_x is not None:
                prev_exit_x = exit_x

            max_h = max(max_h, size.height)
            cursor += size.width
            if i < len(expr.args) - 1:
                cursor += CONTACT_GAP

        width = max(0, cursor - x - (CONTACT_GAP if len(expr.args) > 1 else 0))
        return _Size(
            width,
            max_h,
            merge_x=prev_exit_x,
            merge_y=series_mid_y,
        ), items

    if expr.op == "OR":
        triple = _match_triple_rail_orb(expr)
        if triple and _at_rung_origin(x):
            size, items, _, _ = _layout_triple_rail_orb(*triple, x, y)
            return size, items

        main_y = y + CONTACT_H / 2
        if _at_rung_origin(x) and _use_rung_or_fork(expr):
            return _layout_rung_origin_or_fork(expr, x, y)
        if not _at_rung_origin(x):
            merge_x, items, block_h = _layout_or_at_fork(expr, x, y, main_y)
            return _Size(merge_x - x, block_h, merge_x=merge_x, merge_y=main_y), items

        items: list[Drawable] = []
        branch_rows: list[tuple[float, float, float]] = []
        branch_sizes: list[_Size] = []
        cursor_y = y

        for arg in expr.args:
            size, part = _layout_expr(arg, x, cursor_y)
            bounds = _symbol_bounds(part)
            items.extend(part)
            branch_sizes.append(size)
            if size.merge_y is not None:
                mid_y = size.merge_y
            else:
                mid_y = cursor_y + size.height / 2
            if bounds:
                bx1, _, bx2, _ = bounds
                if size.merge_x is not None:
                    bx2 = max(bx2, size.merge_x)
                branch_rows.append((mid_y, bx1, bx2))
            cursor_y += size.height + BRANCH_GAP

        if not branch_rows:
            return _Size(CONTACT_W, CONTACT_H), items

        main_y = branch_rows[0][0]
        if branch_sizes[0].merge_y is not None:
            main_y = branch_sizes[0].merge_y
        _main_x1, main_bx2 = branch_rows[0][1], branch_rows[0][2]
        if branch_sizes[0].merge_x is not None:
            main_bx2 = max(main_bx2, branch_sizes[0].merge_x)
        bot_y = branch_rows[-1][0]
        merge_x = max(bx2 for _, _, bx2 in branch_rows)
        width = merge_x - x

        if len(branch_rows) > 1:
            left_bus = _wire_v(LEFT_RAIL, main_y, bot_y)
            if left_bus:
                items.append(left_bus)

        for mid_y, bx1, _bx2 in branch_rows:
            entry = _wire_h(LEFT_RAIL, mid_y, bx1)
            if entry:
                items.append(entry)

        # First branch is the main rung line; lower branches merge up into it.
        if main_bx2 < merge_x - 1:
            main_ext = _wire_h(main_bx2, main_y, merge_x)
            if main_ext:
                items.append(main_ext)

        for mid_y, _bx1, bx2 in branch_rows[1:]:
            if bx2 < merge_x - 1:
                stub = _wire_h(bx2, mid_y, merge_x)
                if stub:
                    items.append(stub)
            join = _wire_v(merge_x, mid_y, main_y)
            if join:
                items.append(join)

        total_h = cursor_y - y - (BRANCH_GAP if len(expr.args) > 1 else 0)
        return _Size(width, total_h, merge_x=merge_x, merge_y=main_y), items

    if expr.op == "CMP_NE":
        device = st_name(expr.device)
        return _Size(CONTACT_W, CONTACT_H), [
            Drawable(kind="contact_ne", x=x, y=y, w=CONTACT_W, h=CONTACT_H, text=f"{device}<>0")
        ]

    return _Size(CONTACT_W, CONTACT_H), [
        Drawable(kind="unknown", x=x, y=y, w=CONTACT_W, h=CONTACT_H, text=expr.op)
    ]


def _layout_action(action: RungAction, x: float, y: float) -> tuple[_Size, list[Drawable]]:
    target = st_name(action.target)
    if action.kind == ActionKind.TON_COIL:
        pt = f"T#{action.preset_ms}ms" if action.preset_ms is not None else action.preset or "?"
        return _Size(TIMER_W, TIMER_H), [
            Drawable(
                kind="timer",
                x=x,
                y=y,
                w=TIMER_W,
                h=TIMER_H,
                text=target,
                subtext=pt,
            )
        ]
    if action.kind == ActionKind.MOV:
        src = st_name(action.mov_source)
        dst = st_name(action.mov_dest or action.target)
        return _Size(MOV_W, MOV_H), [
            Drawable(kind="mov", x=x, y=y, w=MOV_W, h=MOV_H, text=f"MOV {src}", subtext=f"→ {dst}")
        ]
    kind_map = {
        ActionKind.OUT: "coil",
        ActionKind.SET: "coil_set",
        ActionKind.RST: "coil_rst",
    }
    return _Size(COIL_W, COIL_H), [
        Drawable(
            kind=kind_map.get(action.kind, "coil"),
            x=x,
            y=y,
            w=COIL_W,
            h=COIL_H,
            text=target,
        )
    ]


def _layout_rung_row(condition: BoolExpr, action: RungAction, base_y: float, coil_x: float) -> tuple[float, list[Drawable]]:
    cond_origin = LEFT_RAIL + LABEL_W
    cond_size, cond_items = _layout_expr(condition, cond_origin, base_y)
    if cond_size.merge_y is not None:
        coil_y = cond_size.merge_y - COIL_H / 2
    else:
        coil_y = base_y + max(0, (cond_size.height - COIL_H) / 2)
    act_size, act_items = _layout_action(action, coil_x, coil_y)

    row_h = max(cond_size.height, act_size.height, COIL_H)
    mid_y = base_y + row_h / 2
    wires: list[Drawable] = []
    symbols: list[Drawable] = list(cond_items) + list(act_items)
    has_or = _expr_has_or(condition)

    if not has_or:
        rail = _wire_h(LEFT_RAIL, mid_y, cond_origin)
        if rail:
            wires.append(rail)

    if cond_size.merge_x is not None and cond_size.merge_y is not None:
        to_coil = _wire_h(cond_size.merge_x, cond_size.merge_y, coil_x)
        if to_coil:
            wires.append(to_coil)
    else:
        cond_bounds = _symbol_bounds(cond_items)
        if cond_bounds:
            _, _, cond_right, _ = cond_bounds
            to_coil = _wire_h(cond_right, mid_y, coil_x)
            if to_coil:
                wires.append(to_coil)
        elif cond_size.width == 0:
            direct = _wire_h(cond_origin, mid_y, coil_x)
            if direct:
                wires.append(direct)

    coil_mid_y = cond_size.merge_y if cond_size.merge_y is not None else mid_y
    from_coil = _wire_h(coil_x + act_size.width, coil_mid_y, coil_x + act_size.width + 20)
    if from_coil:
        wires.append(from_coil)

    return row_h, wires + symbols


def _action_condition(action: RungAction, rung: Rung) -> BoolExpr:
    return action.condition or rung.condition or BoolExpr(op="TRUE")


def _conditions_equal(a: BoolExpr, b: BoolExpr) -> bool:
    return a.to_st() == b.to_st()


def _can_parallel_actions(actions: list[RungAction], rung: Rung) -> bool:
    if len(actions) <= 1:
        return False
    first = _action_condition(actions[0], rung)
    return all(_conditions_equal(first, _action_condition(action, rung)) for action in actions[1:])


def _flatten_and(expr: BoolExpr) -> list[BoolExpr]:
    if expr.op == "AND":
        parts: list[BoolExpr] = []
        for arg in expr.args:
            parts.extend(_flatten_and(arg))
        return parts
    return [expr]


def _extract_common_and_prefix(
    conditions: list[BoolExpr],
) -> tuple[BoolExpr, list[BoolExpr]]:
    if len(conditions) < 2:
        return BoolExpr(op="TRUE"), conditions

    flat = [_flatten_and(cond) for cond in conditions]
    common_len = 0
    limit = min(len(parts) for parts in flat)
    for i in range(limit):
        if all(_conditions_equal(flat[0][i], flat[j][i]) for j in range(1, len(flat))):
            common_len += 1
        else:
            break

    if common_len == 0:
        return BoolExpr(op="TRUE"), conditions

    prefix_parts = flat[0][:common_len]
    if len(prefix_parts) == 1:
        prefix = prefix_parts[0]
    else:
        prefix = BoolExpr(op="AND", args=list(prefix_parts))

    suffixes: list[BoolExpr] = []
    for parts in flat:
        rest = parts[common_len:]
        if not rest:
            suffixes.append(BoolExpr(op="TRUE"))
        elif len(rest) == 1:
            suffixes.append(rest[0])
        else:
            suffixes.append(BoolExpr(op="AND", args=list(rest)))

    return prefix, suffixes


def _can_shared_prefix(actions: list[RungAction], rung: Rung) -> bool:
    if len(actions) <= 1 or _can_parallel_actions(actions, rung):
        return False
    conditions = [_action_condition(action, rung) for action in actions]
    prefix, _ = _extract_common_and_prefix(conditions)
    return prefix.op != "TRUE"


def _group_by_suffix(
    suffixes: list[BoolExpr],
    actions: list[RungAction],
) -> list[tuple[BoolExpr, list[RungAction]]]:
    groups: list[tuple[BoolExpr, list[RungAction]]] = []
    for suffix, action in zip(suffixes, actions):
        if groups and _conditions_equal(groups[-1][0], suffix):
            groups[-1][1].append(action)
        else:
            groups.append((suffix, [action]))
    return groups


def _suffix_path_head(suffix: BoolExpr) -> BoolExpr:
    parts = _flatten_and(suffix)
    if not parts:
        return BoolExpr(op="TRUE")
    return parts[0]


def _suffix_tail_after_head(suffix: BoolExpr) -> BoolExpr:
    parts = _flatten_and(suffix)
    if len(parts) <= 1:
        return BoolExpr(op="TRUE")
    if len(parts) == 2:
        return parts[1]
    return BoolExpr(op="AND", args=list(parts[1:]))


def _parse_sensor_mps_paths(
    suffixes: list[BoolExpr],
    actions: list[RungAction],
) -> list[tuple[BoolExpr, list[tuple[BoolExpr, RungAction]]]] | None:
    """SM400--+--X10--+--T20--(M)  each sensor path has coil + timer sub-branches."""
    path_order: list[str] = []
    path_map: dict[str, list[tuple[BoolExpr, BoolExpr, RungAction]]] = {}

    for suffix, action in zip(suffixes, actions):
        head = _suffix_path_head(suffix)
        if head.op == "TRUE":
            return None
        key = head.to_st()
        if key not in path_map:
            path_map[key] = []
            path_order.append(key)
        tail = _suffix_tail_after_head(suffix)
        path_map[key].append((head, tail, action))

    paths: list[tuple[BoolExpr, list[tuple[BoolExpr, RungAction]]]] = []
    for key in path_order:
        items = path_map[key]
        if len(items) != 2:
            return None
        head = items[0][0]
        if not all(_conditions_equal(h, head) for h, _, _ in items):
            return None
        subs = [(tail, act) for _, tail, act in items]
        if sum(1 for tail, _ in subs if tail.op == "TRUE") != 1:
            return None
        paths.append((head, subs))

    return paths if paths else None


def _can_sensor_mps(actions: list[RungAction], rung: Rung) -> bool:
    if len(actions) < 2 or _can_parallel_actions(actions, rung):
        return False
    conditions = [_action_condition(action, rung) for action in actions]
    prefix, suffixes = _extract_common_and_prefix(conditions)
    if prefix.op == "TRUE":
        return False
    return _parse_sensor_mps_paths(suffixes, actions) is not None


def _layout_sensor_mps_path(
    head: BoolExpr,
    subs: list[tuple[BoolExpr, RungAction]],
    fork_x: float,
    path_y: float,
    coil_x: float,
) -> tuple[float, float, float, list[Drawable], list[Drawable]]:
    """One sensor path: head on row, then fork into coil-line vs timer-line."""
    wires: list[Drawable] = []
    symbols: list[Drawable] = []

    head_x = fork_x + FORK_STUB
    hsize, head_items = _layout_expr(head, head_x, path_y)
    symbols.extend(head_items)
    hbounds = _symbol_bounds(head_items)
    head_end = hsize.merge_x if hsize.merge_x is not None else (hbounds[2] if hbounds else head_x + CONTACT_W)
    fork_x2 = head_end + FORK_W
    if hsize.merge_y is not None:
        path_main_y = hsize.merge_y
    else:
        path_main_y = path_y + CONTACT_H / 2

    entry = _wire_h(fork_x, path_main_y, head_x if hbounds else head_x)
    if entry:
        wires.append(entry)
    to_fork2 = _wire_h(head_end, path_main_y, fork_x2)
    if to_fork2:
        wires.append(to_fork2)

    coil_sub = next((t, a) for t, a in subs if t.op != "TRUE")
    timer_sub = next((t, a) for t, a in subs if t.op == "TRUE")
    coil_tail, coil_action = coil_sub
    _, timer_action = timer_sub

    branch_mids: list[float] = [path_main_y]
    max_right = fork_x2

    tail_x = fork_x2 + FORK_STUB
    tsize_tail, tail_items = _layout_expr(coil_tail, tail_x, path_y)
    symbols.extend(tail_items)
    tbounds = _symbol_bounds(tail_items)
    tail_end = tsize_tail.merge_x if tsize_tail.merge_x is not None else (tbounds[2] if tbounds else tail_x + CONTACT_W)
    max_right = max(max_right, tail_end)

    tail_entry = _wire_h(fork_x2, path_main_y, tail_x if tbounds else tail_x)
    if tail_entry:
        wires.append(tail_entry)

    act_size, act_items = _layout_action(coil_action, coil_x, path_y)
    symbols.extend(act_items)
    to_coil = _wire_h(tail_end, path_main_y, coil_x)
    if to_coil:
        wires.append(to_coil)
    tail_out = _wire_h(coil_x + act_size.width, path_main_y, coil_x + act_size.width + 20)
    if tail_out:
        wires.append(tail_out)
    max_right = max(max_right, coil_x + act_size.width)

    coil_extent = max(hsize.height, tsize_tail.height)
    timer_y = path_y + coil_extent + BRANCH_GAP
    timer_mid = timer_y + COIL_H / 2
    branch_mids.append(timer_mid)

    tsize, titems = _layout_action(timer_action, coil_x, timer_y)
    symbols.extend(titems)
    timer_wire = _wire_h(fork_x2, timer_mid, coil_x)
    if timer_wire:
        wires.append(timer_wire)
    timer_out = _wire_h(coil_x + tsize.width, timer_mid, coil_x + tsize.width + 20)
    if timer_out:
        wires.append(timer_out)
    max_right = max(max_right, coil_x + tsize.width)

    if len(branch_mids) > 1:
        sub_bus = _wire_v(fork_x2, branch_mids[0], branch_mids[-1])
        if sub_bus:
            wires.append(sub_bus)

    path_h = max(coil_extent, timer_y + tsize.height - path_y)
    return path_h, path_main_y, max_right, wires, symbols


def _layout_sensor_mps_rung(
    prefix: BoolExpr,
    actions: list[RungAction],
    suffixes: list[BoolExpr],
    base_y: float,
    coil_x: float,
) -> tuple[float, list[Drawable]]:
    paths = _parse_sensor_mps_paths(suffixes, actions)
    if not paths:
        return CONTACT_H, []

    wires: list[Drawable] = []
    symbols: list[Drawable] = []
    cond_origin = LEFT_RAIL + LABEL_W
    fork_gap = 12

    psize, prefix_items = _layout_expr(prefix, cond_origin, base_y)
    symbols.extend(prefix_items)

    prefix_main_y = psize.merge_y if psize.merge_y is not None else base_y + CONTACT_H / 2
    pbounds = _symbol_bounds(prefix_items)
    if psize.merge_x is not None:
        prefix_end = psize.merge_x
    elif pbounds:
        prefix_end = pbounds[2]
    else:
        prefix_end = cond_origin
    fork_x1 = prefix_end + fork_gap

    rail = _rail_from_left(prefix_main_y, cond_origin)
    if rail:
        wires.append(rail)
    to_fork = _wire_h(prefix_end, prefix_main_y, fork_x1)
    if to_fork:
        wires.append(to_fork)

    tier_bottom = base_y
    path_mids: list[float] = []

    for i, (head, subs) in enumerate(paths):
        path_y = base_y if i == 0 else tier_bottom + BRANCH_GAP
        path_h, path_mid, _, pw, ps = _layout_sensor_mps_path(head, subs, fork_x1, path_y, coil_x)
        wires.extend(pw)
        symbols.extend(ps)
        path_mids.append(path_mid)
        tier_bottom = max(tier_bottom, path_y + path_h)

    if len(path_mids) > 1:
        main_bus = _wire_v(fork_x1, path_mids[0], path_mids[-1])
        if main_bus:
            wires.append(main_bus)

    total_h = max(tier_bottom - base_y, psize.height)
    return total_h, wires + symbols


def _collect_prefix_branches(
    suffixes: list[BoolExpr],
    actions: list[RungAction],
) -> list[tuple[BoolExpr, list[tuple[BoolExpr, RungAction]]]]:
    """Group suffixes by shared path head (e.g. M103|M100 fans into Y2E + T10)."""
    path_order: list[str] = []
    path_map: dict[str, tuple[BoolExpr, list[tuple[BoolExpr, RungAction]]]] = {}

    for suffix, action in zip(suffixes, actions):
        head = _suffix_path_head(suffix)
        tail = _suffix_tail_after_head(suffix)
        key = head.to_st()
        if key not in path_map:
            path_map[key] = (head, [])
            path_order.append(key)
        path_map[key][1].append((tail, action))

    return [path_map[k] for k in path_order]


def _layout_head_parallel_coils(
    head: BoolExpr,
    actions: list[RungAction],
    fork_x: float,
    path_y: float,
    path_mid: float,
    coil_x: float,
) -> tuple[float, float, list[Drawable], list[Drawable]]:
    """One condition from fork_x, then vertically stacked parallel coils."""
    wires: list[Drawable] = []
    symbols: list[Drawable] = []
    fork_gap = 12
    row_h = COIL_H

    cond_x = fork_x + FORK_STUB
    csize, cond_items = _layout_expr(head, cond_x, path_y)
    symbols.extend(cond_items)
    if csize.merge_y is not None:
        path_mid = csize.merge_y
    cbounds = _symbol_bounds(cond_items)
    if csize.merge_x is not None:
        cond_right = csize.merge_x
    elif cbounds:
        cond_right = cbounds[2]
    else:
        cond_right = cond_x + CONTACT_W
    if cbounds:
        entry = _wire_h(fork_x, path_mid, cbounds[0])
        if entry:
            wires.append(entry)

    n = len(actions)
    coil_bus_x = cond_right + fork_gap
    coil_mids: list[float] = []

    for j, action in enumerate(actions):
        act_y = path_y + j * (row_h + ACTION_GAP)
        act_mid = act_y + row_h / 2
        coil_mids.append(act_mid)

        act_size, act_items = _layout_action(action, coil_x, act_y)
        symbols.extend(act_items)

        if j == 0:
            to_coil = _wire_h(cond_right, path_mid, coil_x)
        else:
            to_coil = _wire_h(coil_bus_x, act_mid, coil_x)
        if to_coil:
            wires.append(to_coil)
        tail_out = _wire_h(coil_x + act_size.width, act_mid, coil_x + act_size.width + 20)
        if tail_out:
            wires.append(tail_out)

    if n > 1:
        coil_stub = _wire_h(cond_right, path_mid, coil_bus_x)
        if coil_stub:
            wires.append(coil_stub)
        coil_bus = _wire_v(coil_bus_x, coil_mids[0], coil_mids[-1])
        if coil_bus:
            wires.append(coil_bus)

    branch_h = max(csize.height, path_y + n * row_h + (n - 1) * ACTION_GAP - path_y)
    return branch_h, path_mid, wires, symbols


def _layout_shared_prefix_rung(
    prefix: BoolExpr,
    actions: list[RungAction],
    suffixes: list[BoolExpr],
    base_y: float,
    coil_x: float,
) -> tuple[float, list[Drawable]]:
    """MPS/MPP: common prefix, parallel path heads, inner fork when head is shared (Y2E/T10)."""
    wires: list[Drawable] = []
    symbols: list[Drawable] = []
    cond_origin = LEFT_RAIL + LABEL_W
    fork_gap = 12

    prefix_y = base_y
    psize, prefix_items = _layout_expr(prefix, cond_origin, prefix_y)
    symbols.extend(prefix_items)

    prefix_main_y = psize.merge_y if psize.merge_y is not None else prefix_y + CONTACT_H / 2
    pbounds = _symbol_bounds(prefix_items)
    if psize.merge_x is not None:
        prefix_end = psize.merge_x
    elif pbounds:
        prefix_end = pbounds[2]
    else:
        prefix_end = cond_origin
    fork_x = prefix_end + fork_gap

    to_fork = _wire_h(prefix_end, prefix_main_y, fork_x)
    if to_fork:
        wires.append(to_fork)

    tier_bottom = prefix_y + psize.height
    fork_bus_ys: list[float] = [prefix_main_y]

    rail = _rail_from_left(prefix_main_y, cond_origin)
    if rail:
        wires.append(rail)

    branches = _collect_prefix_branches(suffixes, actions)
    for i, (head, subs) in enumerate(branches):
        if i == 0:
            path_y = prefix_y
            path_mid = prefix_main_y
        else:
            path_y = tier_bottom + BRANCH_GAP
            path_mid = path_y + CONTACT_H / 2

        if (
            len(subs) == 2
            and sum(1 for tail, _ in subs if tail.op == "TRUE") == 1
        ):
            path_h, branch_mid, _, pw, ps = _layout_sensor_mps_path(
                head, subs, fork_x, path_y, coil_x
            )
            wires.extend(pw)
            symbols.extend(ps)
            fork_bus_ys.append(branch_mid)
            tier_bottom = max(tier_bottom, path_y + path_h)
            continue

        if all(tail.op == "TRUE" for tail, _ in subs):
            group_actions = [action for _, action in subs]
            path_h, branch_mid, pw, ps = _layout_head_parallel_coils(
                head, group_actions, fork_x, path_y, path_mid, coil_x
            )
            wires.extend(pw)
            symbols.extend(ps)
            fork_bus_ys.append(branch_mid)
            tier_bottom = max(tier_bottom, path_y + path_h)
            continue

        for j, (tail, action) in enumerate(subs):
            if j > 0:
                path_y = tier_bottom + BRANCH_GAP
                path_mid = path_y + CONTACT_H / 2

            cond = head if tail.op == "TRUE" else BoolExpr(op="AND", args=[head, tail])
            cond_x = fork_x + FORK_STUB
            csize, cond_items = _layout_expr(cond, cond_x, path_y)
            symbols.extend(cond_items)
            if csize.merge_y is not None:
                path_mid = csize.merge_y
            cbounds = _symbol_bounds(cond_items)
            if csize.merge_x is not None:
                cond_right = csize.merge_x
            elif cbounds:
                cond_right = cbounds[2]
            else:
                cond_right = cond_x + CONTACT_W
            if cbounds:
                entry = _wire_h(fork_x, path_mid, cbounds[0])
                if entry:
                    wires.append(entry)

            act_size, act_items = _layout_action(action, coil_x, path_y)
            symbols.extend(act_items)
            to_coil = _wire_h(cond_right, path_mid, coil_x)
            if to_coil:
                wires.append(to_coil)
            tail_out = _wire_h(coil_x + act_size.width, path_mid, coil_x + act_size.width + 20)
            if tail_out:
                wires.append(tail_out)

            branch_h = max(csize.height, act_size.height, COIL_H)
            tier_bottom = max(tier_bottom, path_y + branch_h)
            fork_bus_ys.append(path_mid)

    if len(fork_bus_ys) > 1:
        fork_bus = _wire_v(fork_x, min(fork_bus_ys), max(fork_bus_ys))
        if fork_bus:
            wires.append(fork_bus)

    total_h = tier_bottom - base_y
    return max(total_h, psize.height), wires + symbols


def _layout_parallel_actions(
    condition: BoolExpr,
    actions: list[RungAction],
    base_y: float,
    coil_x: float,
) -> tuple[float, list[Drawable]]:
    """One condition feeding multiple parallel coils (e.g. OUT M2100 + OUT T100)."""
    wires: list[Drawable] = []
    symbols: list[Drawable] = []
    cond_origin = LEFT_RAIL + LABEL_W
    fork_gap = 12

    row_h = COIL_H
    cond_y = base_y
    csize, cond_items = _layout_expr(condition, cond_origin, cond_y)
    symbols.extend(cond_items)

    cond_bounds = _symbol_bounds(cond_items)
    if csize.merge_x is not None:
        cond_right = csize.merge_x
    elif cond_bounds:
        cond_right = cond_bounds[2]
    else:
        cond_right = cond_origin
    contact_mid_y = csize.merge_y if csize.merge_y is not None else cond_y + CONTACT_H / 2
    fork_x = cond_right + fork_gap

    coil_bus_x = cond_right + fork_gap
    coil_mids: list[float] = []
    max_row_bottom = cond_y + csize.height

    for i, action in enumerate(actions):
        act_y = base_y + i * (row_h + ACTION_GAP)
        mid_y = act_y + row_h / 2
        coil_mids.append(mid_y)

        act_size, act_items = _layout_action(action, coil_x, act_y)
        symbols.extend(act_items)

        if i == 0:
            stub = _wire_h(cond_right, contact_mid_y, coil_x)
        else:
            stub = _wire_h(coil_bus_x, mid_y, coil_x)
        if stub:
            wires.append(stub)
        tail = _wire_h(coil_x + act_size.width, mid_y, coil_x + act_size.width + 20)
        if tail:
            wires.append(tail)
        max_row_bottom = max(max_row_bottom, act_y + act_size.height)

    rail = _rail_from_left(contact_mid_y, cond_origin)
    if rail:
        wires.append(rail)

    to_fork = _wire_h(cond_right, contact_mid_y, fork_x)
    if to_fork:
        wires.append(to_fork)

    if len(actions) > 1:
        coil_stub = _wire_h(cond_right, contact_mid_y, coil_bus_x)
        if coil_stub:
            wires.append(coil_stub)
        bus = _wire_v(coil_bus_x, coil_mids[0], coil_mids[-1])
        if bus:
            wires.append(bus)

    total_h = max(csize.height, max_row_bottom - base_y)
    return total_h, wires + symbols


def _layout_rung(
    rung: Rung,
    base_y: float,
    coil_x: float,
) -> tuple[float, list[Drawable]]:
    actions = rung.actions or [
        RungAction(kind=ActionKind.OUT, target="?", condition=rung.condition)
    ]

    if _can_parallel_actions(actions, rung):
        condition = _action_condition(actions[0], rung)
        if _match_triple_rail_orb(condition):
            return _layout_triple_rail_parallel_rung(condition, actions, base_y, coil_x)
        return _layout_parallel_actions(condition, actions, base_y, coil_x)

    if _can_sensor_mps(actions, rung):
        conditions = [_action_condition(action, rung) for action in actions]
        prefix, suffixes = _extract_common_and_prefix(conditions)
        return _layout_sensor_mps_rung(prefix, actions, suffixes, base_y, coil_x)

    if _can_gripper_orb(actions, rung):
        conditions = [_action_condition(action, rung) for action in actions]
        prefix, suffixes = _extract_common_and_prefix(conditions)
        return _layout_gripper_orb_rung(prefix, actions, suffixes, base_y, coil_x)

    if _can_shared_prefix(actions, rung):
        conditions = [_action_condition(action, rung) for action in actions]
        prefix, suffixes = _extract_common_and_prefix(conditions)
        return _layout_shared_prefix_rung(prefix, actions, suffixes, base_y, coil_x)

    row_items: list[Drawable] = []
    row_heights: list[float] = []
    y = base_y
    for action in actions:
        cond = _action_condition(action, rung)
        row_h, items = _layout_rung_row(cond, action, y, coil_x)
        row_heights.append(row_h)
        row_items.extend(items)
        y += row_h + ACTION_GAP

    total_h = sum(row_heights) + ACTION_GAP * (len(row_heights) - 1) if row_heights else CONTACT_H
    return total_h, row_items


def layout_program(program: ProgramIR) -> LadderLayout:
    rungs: list[RungLayout] = []
    y_cursor = 20.0
    max_width = 900.0

    for i, rung in enumerate(program.rungs, start=1):
        coil_x = _coil_x_for_rung(rung, y_cursor)
        total_h, row_items = _layout_rung(rung, y_cursor, coil_x)
        start_y = y_cursor
        label = f"R{i}  step {rung.step or '-'}"
        if rung.label:
            label += f"  | {rung.label}"
        row_items.insert(
            0,
            Drawable(kind="label", x=8, y=start_y + total_h / 2 - 8, w=LABEL_W, h=16, text=label),
        )
        rungs.append(
            RungLayout(
                rung_no=i,
                step=rung.step,
                label=rung.label,
                y=start_y,
                height=total_h,
                drawables=row_items,
            )
        )
        max_width = max(max_width, _drawables_right_edge(row_items) + 40)
        y_cursor += total_h + RUNG_PAD_Y

    return LadderLayout(width=max_width + 40, height=y_cursor + 20, rungs=rungs)
