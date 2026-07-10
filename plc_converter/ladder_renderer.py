from __future__ import annotations

import html
from datetime import datetime
from xml.etree.ElementTree import Element, SubElement, tostring

from .ladder_layout import SYMBOL_KINDS, Drawable, LadderLayout, RungLayout
from .models import ProgramIR

WIRE_KINDS = frozenset({"wire_h", "wire_v"})


def _svg_root(width: float, height: float) -> Element:
    return Element(
        "svg",
        {
            "xmlns": "http://www.w3.org/2000/svg",
            "width": str(int(width)),
            "height": str(int(height)),
            "viewBox": f"0 0 {int(width)} {int(height)}",
        },
    )


def _draw_wire(parent: Element, d: Drawable) -> None:
    SubElement(
        parent,
        "line",
        {
            "x1": str(d.x),
            "y1": str(d.y),
            "x2": str(d.x2),
            "y2": str(d.y2),
            "stroke": "#374151",
            "stroke-width": "2",
            "stroke-linecap": "round",
        },
    )


def _draw_wire_junctions(parent: Element, wires: list[Drawable]) -> None:
    """Small nodes at bus forks so multi-tier junctions read as one connected path."""
    points: dict[tuple[int, int], int] = {}

    def mark(x: float, y: float) -> None:
        key = (round(x * 2), round(y * 2))
        points[key] = points.get(key, 0) + 1

    for d in wires:
        if d.kind == "wire_h":
            mark(d.x, d.y)
            mark(d.x2, d.y2)
        elif d.kind == "wire_v":
            mark(d.x, d.y)
            mark(d.x, d.y2)

    for (kx, ky), count in points.items():
        if count >= 2:
            SubElement(
                parent,
                "circle",
                {
                    "cx": str(kx / 2),
                    "cy": str(ky / 2),
                    "r": "2.5",
                    "fill": "#374151",
                    "stroke": "none",
                },
            )


def _draw_text(
    parent: Element,
    x: float,
    y: float,
    text: str,
    *,
    size: int = 11,
    anchor: str = "middle",
    weight: str = "normal",
) -> None:
    SubElement(
        parent,
        "text",
        {
            "x": str(x),
            "y": str(y),
            "fill": "#111827",
            "font-family": "Consolas, 'Courier New', monospace",
            "font-size": str(size),
            "text-anchor": anchor,
            "font-weight": weight,
        },
    ).text = text


def _draw_contact(parent: Element, d: Drawable, *, nc: bool = False, pulse: bool = False) -> None:
    g = SubElement(parent, "g")
    x, y, w, h = d.x, d.y, d.w, d.h
    mid_y = y + h / 2
    bar_x1 = x + 12
    bar_x2 = x + w - 12

    SubElement(
        g,
        "rect",
        {
            "x": str(x),
            "y": str(y),
            "width": str(w),
            "height": str(h),
            "fill": "#ffffff",
            "stroke": "none",
        },
    )
    SubElement(
        g,
        "line",
        {
            "x1": str(x),
            "y1": str(mid_y),
            "x2": str(bar_x1),
            "y2": str(mid_y),
            "stroke": "#374151",
            "stroke-width": "2",
        },
    )
    SubElement(
        g,
        "line",
        {
            "x1": str(bar_x2),
            "y1": str(mid_y),
            "x2": str(x + w),
            "y2": str(mid_y),
            "stroke": "#374151",
            "stroke-width": "2",
        },
    )
    SubElement(
        g,
        "line",
        {
            "x1": str(bar_x1),
            "y1": str(y + 4),
            "x2": str(bar_x1),
            "y2": str(y + h - 4),
            "stroke": "#2563eb",
            "stroke-width": "2.5",
        },
    )
    SubElement(
        g,
        "line",
        {
            "x1": str(bar_x2),
            "y1": str(y + 4),
            "x2": str(bar_x2),
            "y2": str(y + h - 4),
            "stroke": "#2563eb",
            "stroke-width": "2.5",
        },
    )
    if nc:
        SubElement(
            g,
            "line",
            {
                "x1": str(bar_x1 - 2),
                "y1": str(y + h - 4),
                "x2": str(bar_x2 + 2),
                "y2": str(y + 4),
                "stroke": "#2563eb",
                "stroke-width": "2",
            },
        )
    if pulse:
        cx = x + w / 2
        cy = mid_y + 1
        SubElement(
            g,
            "polygon",
            {
                "points": f"{cx},{cy - 6} {cx - 4.5},{cy + 5} {cx + 4.5},{cy + 5}",
                "fill": "#2563eb",
                "stroke": "none",
            },
        )
    label = d.text
    _draw_text(g, x + w / 2, y - 2, label, size=10, weight="bold")


def _draw_coil(parent: Element, d: Drawable, prefix: str = "") -> None:
    g = SubElement(parent, "g")
    x, y, w, h = d.x, d.y, d.w, d.h
    cx = x + w / 2
    cy = y + h / 2
    rx = w / 2 - 6
    ry = h / 2 - 2
    mid_y = cy

    SubElement(
        g,
        "rect",
        {
            "x": str(x),
            "y": str(y),
            "width": str(w),
            "height": str(h),
            "fill": "#ffffff",
            "stroke": "none",
        },
    )
    SubElement(
        g,
        "line",
        {
            "x1": str(x),
            "y1": str(mid_y),
            "x2": str(cx - rx),
            "y2": str(mid_y),
            "stroke": "#374151",
            "stroke-width": "2",
        },
    )
    SubElement(
        g,
        "line",
        {
            "x1": str(cx + rx),
            "y1": str(mid_y),
            "x2": str(x + w),
            "y2": str(mid_y),
            "stroke": "#374151",
            "stroke-width": "2",
        },
    )
    SubElement(
        g,
        "ellipse",
        {
            "cx": str(cx),
            "cy": str(cy),
            "rx": str(rx),
            "ry": str(ry),
            "fill": "#fff",
            "stroke": "#dc2626",
            "stroke-width": "2",
        },
    )
    text = f"{prefix}{d.text}" if prefix else d.text
    _draw_text(g, cx, cy + 4, text, size=10, weight="bold")


def _draw_timer(parent: Element, d: Drawable) -> None:
    g = SubElement(parent, "g")
    SubElement(
        g,
        "rect",
        {
            "x": str(d.x),
            "y": str(d.y),
            "width": str(d.w),
            "height": str(d.h),
            "fill": "#fffbeb",
            "stroke": "#d97706",
            "stroke-width": "2",
            "rx": "4",
        },
    )
    _draw_text(g, d.x + d.w / 2, d.y + 16, d.text, size=10, weight="bold")
    if d.subtext:
        _draw_text(g, d.x + d.w / 2, d.y + 30, d.subtext, size=9)


def _draw_mov(parent: Element, d: Drawable) -> None:
    g = SubElement(parent, "g")
    SubElement(
        g,
        "rect",
        {
            "x": str(d.x),
            "y": str(d.y),
            "width": str(d.w),
            "height": str(d.h),
            "fill": "#ecfeff",
            "stroke": "#0891b2",
            "stroke-width": "2",
            "rx": "4",
        },
    )
    _draw_text(g, d.x + d.w / 2, d.y + 15, d.text, size=10)
    if d.subtext:
        _draw_text(g, d.x + d.w / 2, d.y + 29, d.subtext, size=9)


def _draw_rung_separator(parent: Element, rung: RungLayout) -> None:
    y = rung.y + rung.height + 6
    SubElement(
        parent,
        "line",
        {
            "x1": "8",
            "y1": str(y),
            "x2": "9999",
            "y2": str(y),
            "stroke": "#e5e7eb",
            "stroke-width": "1",
        },
    )


def _draw_power_rails(parent: Element, height: float) -> None:
    SubElement(
        parent,
        "line",
        {
            "x1": "16",
            "y1": "10",
            "x2": "16",
            "y2": str(height - 10),
            "stroke": "#374151",
            "stroke-width": "3",
        },
    )


def _render_symbol(parent: Element, d: Drawable) -> None:
    if d.kind == "contact_no":
        _draw_contact(parent, d, nc=False)
    elif d.kind == "contact_pls":
        _draw_contact(parent, d, nc=False, pulse=True)
    elif d.kind == "contact_nc":
        _draw_contact(parent, d, nc=True)
    elif d.kind == "contact_ne":
        _draw_contact(parent, d, nc=False)
    elif d.kind == "coil":
        _draw_coil(parent, d)
    elif d.kind == "coil_set":
        _draw_coil(parent, d, prefix="S ")
    elif d.kind == "coil_rst":
        _draw_coil(parent, d, prefix="R ")
    elif d.kind == "timer":
        _draw_timer(parent, d)
    elif d.kind == "mov":
        _draw_mov(parent, d)
    elif d.kind == "label":
        _draw_text(parent, d.x, d.y, d.text, size=10, anchor="start")
    elif d.kind == "unknown":
        _draw_text(parent, d.x, d.y, d.text, size=10, anchor="start")


def _render_rung(parent: Element, rung: RungLayout) -> None:
    wires = [d for d in rung.drawables if d.kind in WIRE_KINDS]
    symbols = [d for d in rung.drawables if d.kind in SYMBOL_KINDS]
    labels = [d for d in rung.drawables if d.kind == "label"]

    wire_layer = SubElement(parent, "g", {"class": "wires"})
    symbol_layer = SubElement(parent, "g", {"class": "symbols"})
    label_layer = SubElement(parent, "g", {"class": "labels"})

    for d in wires:
        _draw_wire(wire_layer, d)
    if wires:
        _draw_wire_junctions(wire_layer, wires)
    for d in symbols:
        _render_symbol(symbol_layer, d)
    for d in labels:
        _render_symbol(label_layer, d)

    _draw_rung_separator(parent, rung)


def render_svg(layout: LadderLayout, program: ProgramIR) -> str:
    root = _svg_root(layout.width, layout.height)

    title = SubElement(
        root,
        "text",
        {
            "x": "24",
            "y": "14",
            "fill": "#111827",
            "font-family": "Segoe UI, sans-serif",
            "font-size": "13",
            "font-weight": "bold",
        },
    )
    title.text = f"{program.name}  |  {program.project}"

    _draw_power_rails(root, layout.height)

    for rung in layout.rungs:
        _render_rung(root, rung)

    return '<?xml version="1.0" encoding="UTF-8"?>\n' + tostring(root, encoding="unicode")


def render_html(layout: LadderLayout, program: ProgramIR, svg: str) -> str:
    safe_name = html.escape(program.name)
    safe_project = html.escape(program.project or "")
    rung_count = len(layout.rungs)
    unsupported = html.escape("\n".join(program.unsupported) or "없음")
    generated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return f"""<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8" />
  <meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{safe_name} Ladder View</title>
  <style>
    body {{ margin: 0; font-family: "Segoe UI", sans-serif; background: #f8fafc; color: #111827; }}
    header {{ padding: 16px 20px; background: #111827; color: #fff; }}
    header h1 {{ margin: 0 0 4px; font-size: 18px; }}
    header p {{ margin: 0; font-size: 13px; color: #cbd5e1; }}
    .wrap {{ padding: 16px; overflow: auto; }}
    .panel {{ background: #fff; border: 1px solid #e5e7eb; border-radius: 8px; padding: 12px; margin-bottom: 12px; }}
    .legend span {{ display: inline-block; margin-right: 14px; font-size: 12px; }}
    .contact {{ color: #2563eb; }}
    .coil {{ color: #dc2626; }}
    .timer {{ color: #d97706; }}
    svg {{ display: block; width: auto; height: auto; max-width: none; }}
  </style>
</head>
<body>
  <header>
    <h1>{safe_name}</h1>
    <p>{safe_project} · rung {rung_count}개 · 생성 {generated_at}</p>
  </header>
  <div class="wrap">
    <div class="panel legend">
      <span class="contact">| | 접점 NO / /NC</span>
      <span class="contact">|↑| 펄스 접점 (LDP)</span>
      <span class="coil">( ) 코일 OUT</span>
      <span class="coil">S SET / R RST</span>
      <span class="timer">▣ 타이머</span>
    </div>
    <div class="panel">
      {svg}
    </div>
    <div class="panel">
      <strong>파싱 경고</strong>
      <pre style="white-space: pre-wrap; font-size: 12px;">{unsupported}</pre>
    </div>
  </div>
</body>
</html>
"""
