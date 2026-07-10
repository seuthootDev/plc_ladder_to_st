from __future__ import annotations

import re


def device_to_st_name(device: str) -> str:
    return device.upper().replace(".", "_")


def infer_data_type(device: str) -> str:
    device = device.upper()
    if device.startswith(("X", "Y", "M", "L", "SM")):
        return "BOOL"
    if device.startswith("T"):
        return "TON"
    if device.startswith("C"):
        return "CTU"
    if "." in device:
        return "BOOL"
    if device.startswith(("D", "SD", "W", "R")):
        return "WORD"
    if device.startswith("K"):
        return "CONST"
    return "BOOL"


def preset_to_ms(preset: str, timer_base_ms: int = 100) -> int | None:
    """Convert Mitsubishi K constant to milliseconds (default 100ms base)."""
    preset = preset.upper().strip()
    if not preset.startswith("K"):
        return None
    try:
        value = int(preset[1:])
    except ValueError:
        return None
    return value * timer_base_ms
