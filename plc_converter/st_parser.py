from __future__ import annotations



import re

from dataclasses import dataclass

from pathlib import Path



from .models import ActionKind, BoolExpr, ProgramIR, Rung, RungAction, st_name



RUNG_HEADER = re.compile(

    r"\(\*\s*---\s*Rung\s+(\d+)\s*,\s*step\s+(\d+)(?:\s*\|\s*([^*]+?))?\s*---\s*\*\)",

    re.IGNORECASE,

)

META_PROJECT = re.compile(r"\(\*\s*Project:\s*(.+?)\s*\*\)", re.IGNORECASE)

META_CPU = re.compile(r"\(\*\s*CPU:\s*(.+?)\s*\*\)", re.IGNORECASE)

META_NAME = re.compile(r"\(\*\s*Generated ST from context:\s*(.+?)\s*\*\)", re.IGNORECASE)

PROGRAM_NAME = re.compile(r"^\s*PROGRAM\s+(\w+)", re.MULTILINE | re.IGNORECASE)

PT_LITERAL = re.compile(r"T#(\d+)(ms|s)", re.IGNORECASE)





@dataclass

class _Token:

    kind: str

    value: str





def _strip_comments(text: str) -> str:

    return re.sub(r"\(\*.*?\*\)", "", text, flags=re.DOTALL)





def extract_implementation(st_text: str) -> str:

    """Return implementation body (rung logic) from a full or partial ST file."""

    if RUNG_HEADER.search(st_text):

        start = RUNG_HEADER.search(st_text).start()

        return st_text[start:]



    after_var = re.split(r"\bEND_VAR\b", st_text, maxsplit=1, flags=re.IGNORECASE)

    if len(after_var) > 1:

        return after_var[1]



    return st_text





def _tokenize_bool(text: str) -> list[_Token]:

    tokens: list[_Token] = []

    i = 0

    while i < len(text):

        ch = text[i]

        if ch.isspace():

            i += 1

            continue

        if ch in "()":

            tokens.append(_Token("LPAREN" if ch == "(" else "RPAREN", ch))

            i += 1

            continue

        if text[i : i + 2] == "<>":

            tokens.append(_Token("NE", "<>"))

            i += 2

            continue

        word_m = re.match(r"[A-Za-z_][A-Za-z0-9_]*", text[i:])

        if word_m:

            word = word_m.group(0)

            upper = word.upper()

            if upper == "AND":

                tokens.append(_Token("AND", upper))

            elif upper == "OR":

                tokens.append(_Token("OR", upper))

            elif upper == "NOT":

                tokens.append(_Token("NOT", upper))

            elif upper == "TRUE":

                tokens.append(_Token("TRUE", upper))

            else:

                tokens.append(_Token("IDENT", word))

            i += len(word)

            continue

        raise ValueError(f"unexpected character in condition: {text[i:]!r}")

    return tokens





class _BoolParser:

    def __init__(self, tokens: list[_Token]) -> None:

        self.tokens = tokens

        self.pos = 0



    def _peek(self) -> _Token | None:

        return self.tokens[self.pos] if self.pos < len(self.tokens) else None



    def _eat(self, kind: str | None = None) -> _Token:

        tok = self._peek()

        if tok is None:

            raise ValueError("unexpected end of condition")

        if kind and tok.kind != kind:

            raise ValueError(f"expected {kind}, got {tok.kind}")

        self.pos += 1

        return tok



    def parse(self) -> BoolExpr:

        expr = self._parse_or()

        if self._peek() is not None:

            raise ValueError(f"trailing tokens in condition: {self.tokens[self.pos:]}")

        return expr



    def _parse_or(self) -> BoolExpr:

        left = self._parse_and()

        while self._peek() and self._peek().kind == "OR":

            self._eat("OR")

            right = self._parse_and()

            left = _combine_bool(left, "OR", right)

        return left



    def _parse_and(self) -> BoolExpr:

        left = self._parse_unary()

        while self._peek() and self._peek().kind == "AND":

            self._eat("AND")

            right = self._parse_unary()

            left = _combine_bool(left, "AND", right)

        return left



    def _parse_unary(self) -> BoolExpr:

        if self._peek() and self._peek().kind == "NOT":

            self._eat("NOT")

            self._eat("LPAREN")

            inner = self._parse_or()

            self._eat("RPAREN")

            return BoolExpr(op="NOT", args=[inner])

        return self._parse_primary()



    def _parse_primary(self) -> BoolExpr:

        tok = self._peek()

        if tok is None:

            raise ValueError("empty condition")

        if tok.kind == "TRUE":

            self._eat("TRUE")

            return BoolExpr(op="TRUE")

        if tok.kind == "IDENT":

            self._eat("IDENT")

            if self._peek() and self._peek().kind == "NE":

                self._eat("NE")

                rhs = self._parse_primary()

                return BoolExpr(op="CMP_NE", device=tok.value, args=[rhs])

            return BoolExpr(op="CONTACT", device=tok.value)

        if tok.kind == "LPAREN":

            self._eat("LPAREN")

            expr = self._parse_or()

            self._eat("RPAREN")

            return expr

        raise ValueError(f"unexpected token: {tok}")





def _combine_bool(left: BoolExpr, op: str, right: BoolExpr) -> BoolExpr:

    if left.op == op:

        left.args.append(right)

        return left

    return BoolExpr(op=op, args=[left, right])





def parse_bool_expr(text: str) -> BoolExpr:

    cleaned = _strip_comments(text).strip()

    if not cleaned:

        return BoolExpr(op="TRUE")

    tokens = _tokenize_bool(cleaned)

    return _BoolParser(tokens).parse()





def _parse_pt_literal(text: str) -> int | None:

    m = PT_LITERAL.search(text)

    if not m:

        return None

    amount = int(m.group(1))

    unit = m.group(2).lower()

    return amount * 1000 if unit == "s" else amount





def _split_if_blocks(body: str) -> list[tuple[str, str]]:

    blocks: list[tuple[str, str]] = []

    upper = body.upper()

    pos = 0

    while pos < len(body):

        idx = upper.find("IF ", pos)

        if idx < 0:

            break

        then_idx = upper.find(" THEN", idx)

        if then_idx < 0:

            break

        cond = body[idx + 3 : then_idx].strip()

        end_idx = upper.find("END_IF", then_idx)

        if end_idx < 0:

            break

        stmt_body = body[then_idx + 5 : end_idx].strip()

        blocks.append((cond, stmt_body))

        pos = end_idx + len("END_IF")

    return blocks





def _parse_action(cond_text: str, body: str) -> list[RungAction]:

    condition = parse_bool_expr(cond_text)

    body = body.strip()

    if not body:

        return []



    out_m = re.match(

        r"^([A-Za-z_][A-Za-z0-9_]*)\s*:=\s*TRUE\s*;\s*ELSE\s+\1\s*:=\s*FALSE\s*;?\s*$",

        _strip_comments(body).replace("\n", " "),

        re.IGNORECASE,

    )

    if out_m:

        return [

            RungAction(

                kind=ActionKind.OUT,

                target=st_name(out_m.group(1)),

                condition=condition,

            )

        ]



    assign_true = re.match(

        r"^([A-Za-z_][A-Za-z0-9_]*)\s*:=\s*TRUE\s*;?\s*$",

        body,

        re.IGNORECASE,

    )

    if assign_true:

        return [

            RungAction(

                kind=ActionKind.SET,

                target=st_name(assign_true.group(1)),

                condition=condition,

            )

        ]



    assign_false = re.match(

        r"^([A-Za-z_][A-Za-z0-9_]*)\s*:=\s*FALSE\s*;?\s*$",

        body,

        re.IGNORECASE,

    )

    if assign_false:

        return [

            RungAction(

                kind=ActionKind.RST,

                target=st_name(assign_false.group(1)),

                condition=condition,

            )

        ]



    mov_m = re.match(

        r"^([A-Za-z_][A-Za-z0-9_]*)\s*:=\s*([A-Za-z_][A-Za-z0-9_]*)\s*;?\s*$",

        body,

        re.IGNORECASE,

    )

    if mov_m:

        return [

            RungAction(

                kind=ActionKind.MOV,

                target=mov_m.group(1),

                mov_dest=mov_m.group(1),

                mov_source=mov_m.group(2),

                condition=condition,

            )

        ]



    ton_m = re.search(

        r"([A-Za-z_][A-Za-z0-9_]*)\s*\(\s*IN\s*:=\s*TRUE\s*,\s*PT\s*:=\s*(T#[^)]+)\s*\)",

        body,

        re.IGNORECASE,

    )

    if ton_m:

        return [

            RungAction(

                kind=ActionKind.TON_COIL,

                target=st_name(ton_m.group(1)),

                preset_ms=_parse_pt_literal(ton_m.group(2)),

                condition=condition,

            )

        ]



    return []





def parse_rung_body(body: str) -> list[RungAction]:

    actions: list[RungAction] = []

    for cond, stmt_body in _split_if_blocks(body):

        actions.extend(_parse_action(cond, stmt_body))

    return actions





def parse_st(

    st_text: str,

    *,

    name: str = "",

    project: str = "",

    cpu: str = "",

) -> ProgramIR:

    if not name:

        m = META_NAME.search(st_text) or PROGRAM_NAME.search(st_text)

        name = m.group(1).strip() if m else "Program"

    if not project:

        m = META_PROJECT.search(st_text)

        project = m.group(1).strip() if m else ""

    if not cpu:

        m = META_CPU.search(st_text)

        cpu = m.group(1).strip() if m else ""



    impl = extract_implementation(st_text)

    program = ProgramIR(name=name, project=project, cpu=cpu)

    headers = list(RUNG_HEADER.finditer(impl))

    if not headers:

        program.unsupported.append("no rung headers found in ST")

        return program



    for idx, match in enumerate(headers):

        rung_no = int(match.group(1))

        step = int(match.group(2))

        label = (match.group(3) or "").strip()

        start = match.end()

        end = headers[idx + 1].start() if idx + 1 < len(headers) else len(impl)

        body = impl[start:end].strip()

        actions = parse_rung_body(body)

        if not actions:

            program.unsupported.append(f"Rung {rung_no}: no actions parsed")

            program.rungs.append(

                Rung(

                    step=step,

                    label=label,

                    condition=BoolExpr(op="TRUE"),

                    actions=[],

                )

            )

            continue

        program.rungs.append(

            Rung(

                step=step,

                label=label,

                condition=BoolExpr(op="TRUE"),

                actions=actions,

            )

        )

        _ = rung_no

    return program





def parse_st_file(path: str | Path) -> ProgramIR:

    text = Path(path).read_text(encoding="utf-8")

    return parse_st(text)

