from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any


@dataclass
class ProgramInfo:
    program_no: str
    name: str
    execute_type: str = "Scan"


@dataclass
class TimerPreset:
    step: int
    timer: str
    preset: str


@dataclass
class IlInstruction:
    step: int | None
    label: str
    mnemonic: str
    operand: str
    preset: str = ""
    mov_dest: str = ""


@dataclass
class VarHint:
    device: str
    comment: str
    data_type: str
    st_name: str


@dataclass
class ProgramContext:
    program_no: str
    program_name: str
    pou_name: str
    project: str
    cpu: str
    csv_path: str
    line_labels: list[dict[str, Any]]
    instructions: list[dict[str, Any]]
    devices_used: list[str]
    device_comments: dict[str, str]
    timer_presets: list[dict[str, Any]]
    var_hints: list[dict[str, Any]]
    ladder_devices: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class ActionKind(str, Enum):
    OUT = "OUT"
    SET = "SET"
    RST = "RST"
    MOV = "MOV"
    TON_COIL = "TON_COIL"


def st_name(device: str) -> str:
    return device.upper().replace(".", "_")


@dataclass
class BoolExpr:
    op: str
    device: str = ""
    args: list[BoolExpr] = field(default_factory=list)

    def copy(self) -> BoolExpr:
        if self.op in {"CONTACT", "TRUE", "CMP_NE"}:
            return BoolExpr(op=self.op, device=self.device, args=[a.copy() for a in self.args])
        return BoolExpr(op=self.op, device=self.device, args=[a.copy() for a in self.args])

    def to_st(self) -> str:
        if self.op == "CONTACT":
            return st_name(self.device)
        if self.op == "NOT":
            return f"NOT ({self.args[0].to_st()})"
        if self.op == "AND":
            return " AND ".join(f"({a.to_st()})" for a in self.args)
        if self.op == "OR":
            return " OR ".join(f"({a.to_st()})" for a in self.args)
        if self.op == "TRUE":
            return "TRUE"
        if self.op == "CMP_NE":
            return f"({st_name(self.device)} <> {self.args[0].to_st()})"
        raise ValueError(self.op)


@dataclass
class RungAction:
    kind: ActionKind
    target: str
    preset: str = ""
    preset_ms: int | None = None
    mov_source: str = ""
    mov_dest: str = ""
    condition: BoolExpr | None = None


@dataclass
class Rung:
    step: int | None
    label: str
    condition: BoolExpr
    actions: list[RungAction] = field(default_factory=list)


@dataclass
class ProgramIR:
    name: str
    project: str = ""
    cpu: str = ""
    rungs: list[Rung] = field(default_factory=list)
    unsupported: list[str] = field(default_factory=list)
