from __future__ import annotations

from .models import (
    ActionKind,
    BoolExpr,
    ProgramIR,
    Rung,
    RungAction,
)

CONTACT_LD = {"LD", "LDI", "LDP", "LDF", "LD<>"}
CONTACT_AND = {"AND", "ANI", "ANDP", "ANDF"}
CONTACT_OR = {"OR", "ORI", "ORP", "ORF"}
COIL_OPS = {"OUT", "SET", "RST"}


def _is_timer(device: str) -> bool:
    return device.upper().startswith("T") and device[1:].isdigit()


def _contact(mnemonic: str, device: str) -> BoolExpr:
    if mnemonic == "LD<>":
        return BoolExpr(op="CMP_NE", device=device, args=[BoolExpr(op="CONTACT", device="K0")])
    if mnemonic in {"LDI", "ANI"} or mnemonic.endswith("F"):
        return BoolExpr(op="NOT", args=[BoolExpr(op="CONTACT", device=device)])
    if mnemonic in {"LDP", "ANDP", "ORP"}:
        return BoolExpr(op="CONTACT", device=f"{device}_PLS")
    return BoolExpr(op="CONTACT", device=device)


def _combine(left: BoolExpr | None, op: str, right: BoolExpr) -> BoolExpr:
    if left is None:
        return right
    if left.op == op:
        left.args.append(right)
        return left
    return BoolExpr(op=op, args=[left, right])


class IlRungBuilder:
    def __init__(self) -> None:
        self.acc: BoolExpr | None = None
        self.stack: list[BoolExpr] = []
        self.actions: list[RungAction] = []
        self.unsupported: list[str] = []
        self._rung_started = False
        self._pending_mpp_ld = False

    def _condition(self) -> BoolExpr:
        return self.acc or BoolExpr(op="TRUE")

    def _flush_action(self, inst: dict) -> None:
        self._clear_pending_mpp_ld()
        m = inst["mnemonic"]
        operand = inst.get("operand", "")
        preset = inst.get("preset", "") or ""
        preset_ms = inst.get("preset_ms")
        cond = self._condition()

        if m in COIL_OPS:
            kind = ActionKind.TON_COIL if _is_timer(operand) else ActionKind(m)
            self.actions.append(
                RungAction(
                    kind=kind,
                    target=operand,
                    preset=preset,
                    preset_ms=preset_ms,
                    condition=cond.copy(),
                )
            )
            return

        if m == "MOV":
            mov_dest = inst.get("mov_dest", "") or ""
            self.actions.append(
                RungAction(
                    kind=ActionKind.MOV,
                    target=mov_dest or operand,
                    mov_source=operand,
                    mov_dest=mov_dest,
                    condition=cond.copy(),
                )
            )
            if not mov_dest:
                self.unsupported.append(
                    f"MOV missing destination at step {inst.get('step')}: {operand}"
                )
            return

        self.unsupported.append(f"unsupported action: {m} {operand}")

    def _clear_pending_mpp_ld(self) -> None:
        self._pending_mpp_ld = False

    def _begin_ld(self, mnemonic: str, device: str) -> None:
        self._pending_mpp_ld = False
        if self._rung_started:
            if self.acc is not None:
                self.stack.append(self.acc.copy())
        else:
            self._rung_started = True

        self.acc = _contact(mnemonic, device)

    def process(self, inst: dict) -> None:
        m = inst.get("mnemonic", "").upper()
        d = inst.get("operand", "")

        if m in CONTACT_LD:
            self._begin_ld(m, d)
            return

        if m in CONTACT_AND:
            self._clear_pending_mpp_ld()
            self.acc = _combine(self.acc, "AND", _contact(m, d))
            return

        if m in CONTACT_OR:
            self._clear_pending_mpp_ld()
            self.acc = _combine(self.acc, "OR", _contact(m, d))
            return

        if m == "INV":
            self._clear_pending_mpp_ld()
            if self.acc is None:
                self.unsupported.append("INV with empty acc")
            else:
                self.acc = BoolExpr(op="NOT", args=[self.acc.copy()])
            return

        if m == "MPS":
            if self.acc is None:
                self.unsupported.append("MPS with empty acc")
            else:
                self.stack.append(self.acc.copy())
            return

        if m == "MRD":
            if not self.stack:
                self.unsupported.append("MRD with empty stack")
            else:
                self.acc = self.stack[-1].copy()
                self._pending_mpp_ld = True
            return

        if m == "MPP":
            if not self.stack:
                self.unsupported.append("MPP with empty stack")
            else:
                self.acc = self.stack.pop()
                self._pending_mpp_ld = True
            return

        if m == "ORB":
            self._clear_pending_mpp_ld()
            if not self.stack:
                self.unsupported.append("ORB with empty stack")
            else:
                left = self.stack.pop()
                self.acc = _combine(left, "OR", self.acc or BoolExpr(op="TRUE"))
            return

        if m == "ANB":
            self._clear_pending_mpp_ld()
            if not self.stack:
                self.unsupported.append("ANB with empty stack")
            else:
                left = self.stack.pop()
                self.acc = _combine(left, "AND", self.acc or BoolExpr(op="TRUE"))
            return

        if m in COIL_OPS or m == "MOV":
            self._flush_action(inst)
            return

        if m == "END":
            return

        self.unsupported.append(f"unsupported: {m} {d}")

    def build_rung(self, step: int | None, label: str) -> Rung:
        rung = Rung(step=step, label=label, condition=self._condition(), actions=list(self.actions))
        self.acc = None
        self.stack.clear()
        self.actions.clear()
        self._rung_started = False
        self._pending_mpp_ld = False
        return rung


def build_program_ir(context: dict) -> ProgramIR:
    program = ProgramIR(
        name=context["pou_name"],
        project=context.get("project", ""),
        cpu=context.get("cpu", ""),
    )
    builder = IlRungBuilder()
    current_step: int | None = None
    current_label = ""

    def flush_rung() -> None:
        nonlocal current_label
        if not builder.actions and builder.acc is None:
            return
        program.rungs.append(builder.build_rung(current_step, current_label))
        current_label = ""

    line_step_by_label = {
        item["label"]: item["step"]
        for item in context.get("line_labels", [])
        if item.get("label")
    }

    for inst in context.get("instructions", []):
        m = inst.get("mnemonic", "").upper()
        if m == "END":
            flush_rung()
            break

        if m in CONTACT_LD:
            if builder.actions and not builder.stack and not builder._pending_mpp_ld:
                flush_rung()
            if not builder._rung_started:
                label = inst.get("label") or ""
                if label and label in line_step_by_label:
                    current_step = line_step_by_label[label]
                else:
                    current_step = inst.get("step")
                if label:
                    current_label = label

        builder.process(inst)

    flush_rung()
    program.unsupported.extend(builder.unsupported)
    return program
