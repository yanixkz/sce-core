from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, List, Tuple

from sce.core.types import State


class ConstraintDSLError(ValueError):
    """Raised when a DSL constraint cannot be parsed or compiled."""


Token = Tuple[str, Any]


@dataclass(frozen=True)
class Identifier:
    name: str


@dataclass(frozen=True)
class Literal:
    value: Any


@dataclass(frozen=True)
class UnaryOp:
    op: str
    operand: Any


@dataclass(frozen=True)
class BinaryOp:
    op: str
    left: Any
    right: Any


class _Tokenizer:
    def __init__(self, source: str) -> None:
        self.source = source
        self.length = len(source)
        self.index = 0

    def tokenize(self) -> List[Token]:
        tokens: List[Token] = []
        while self.index < self.length:
            ch = self.source[self.index]
            if ch.isspace():
                self.index += 1
                continue

            if ch in ("(", ")"):
                tokens.append((ch, ch))
                self.index += 1
                continue

            two_char = self.source[self.index : self.index + 2]
            if two_char in {"==", "!=", "<=", ">="}:
                tokens.append(("OP", two_char))
                self.index += 2
                continue

            if ch in {"<", ">"}:
                tokens.append(("OP", ch))
                self.index += 1
                continue

            if ch in {'"', "'"}:
                tokens.append(("STRING", self._read_string(ch)))
                continue

            if ch.isdigit() or (ch == "-" and self._peek_is_digit()):
                tokens.append(("NUMBER", self._read_number()))
                continue

            if ch.isalpha() or ch == "_":
                word = self._read_word()
                upper = word.upper()
                if upper in {"AND", "OR", "NOT"}:
                    tokens.append((upper, upper))
                elif upper == "TRUE":
                    tokens.append(("BOOL", True))
                elif upper == "FALSE":
                    tokens.append(("BOOL", False))
                else:
                    tokens.append(("IDENT", word))
                continue

            raise ConstraintDSLError(f"Unexpected character at position {self.index}: {ch!r}")

        tokens.append(("EOF", None))
        return tokens

    def _peek_is_digit(self) -> bool:
        return self.index + 1 < self.length and self.source[self.index + 1].isdigit()

    def _read_word(self) -> str:
        start = self.index
        while self.index < self.length and (self.source[self.index].isalnum() or self.source[self.index] == "_"):
            self.index += 1
        return self.source[start:self.index]

    def _read_number(self) -> int | float:
        start = self.index
        if self.source[self.index] == "-":
            self.index += 1
        while self.index < self.length and self.source[self.index].isdigit():
            self.index += 1
        if self.index < self.length and self.source[self.index] == ".":
            self.index += 1
            if self.index >= self.length or not self.source[self.index].isdigit():
                raise ConstraintDSLError("Invalid number format")
            while self.index < self.length and self.source[self.index].isdigit():
                self.index += 1
            return float(self.source[start:self.index])
        return int(self.source[start:self.index])

    def _read_string(self, quote: str) -> str:
        self.index += 1
        result: List[str] = []
        while self.index < self.length:
            ch = self.source[self.index]
            if ch == "\\":
                self.index += 1
                if self.index >= self.length:
                    raise ConstraintDSLError("Unterminated escape sequence in string")
                result.append(self.source[self.index])
                self.index += 1
                continue
            if ch == quote:
                self.index += 1
                return "".join(result)
            result.append(ch)
            self.index += 1
        raise ConstraintDSLError("Unterminated string literal")


class _Parser:
    def __init__(self, tokens: List[Token]) -> None:
        self.tokens = tokens
        self.index = 0

    def parse(self) -> Any:
        node = self._parse_or()
        self._expect("EOF")
        return node

    def _parse_or(self) -> Any:
        node = self._parse_and()
        while self._match("OR"):
            right = self._parse_and()
            node = BinaryOp("OR", node, right)
        return node

    def _parse_and(self) -> Any:
        node = self._parse_not()
        while self._match("AND"):
            right = self._parse_not()
            node = BinaryOp("AND", node, right)
        return node

    def _parse_not(self) -> Any:
        if self._match("NOT"):
            return UnaryOp("NOT", self._parse_not())
        return self._parse_comparison()

    def _parse_comparison(self) -> Any:
        left = self._parse_primary()
        if self._peek_type() == "OP":
            op = self._consume("OP")[1]
            right = self._parse_primary()
            return BinaryOp(op, left, right)
        return left

    def _parse_primary(self) -> Any:
        token_type, token_value = self._peek()
        if token_type == "(":
            self._consume("(")
            node = self._parse_or()
            self._expect(")")
            return node
        if token_type == "IDENT":
            self._consume("IDENT")
            return Identifier(token_value)
        if token_type in {"NUMBER", "STRING", "BOOL"}:
            self._consume(token_type)
            return Literal(token_value)
        raise ConstraintDSLError(f"Unexpected token: {token_type}")

    def _peek(self) -> Token:
        return self.tokens[self.index]

    def _peek_type(self) -> str:
        return self.tokens[self.index][0]

    def _consume(self, expected: str) -> Token:
        token = self.tokens[self.index]
        if token[0] != expected:
            raise ConstraintDSLError(f"Expected token {expected}, got {token[0]}")
        self.index += 1
        return token

    def _expect(self, expected: str) -> None:
        self._consume(expected)

    def _match(self, token_type: str) -> bool:
        if self._peek_type() == token_type:
            self.index += 1
            return True
        return False


def compile_constraint_dsl(expression: str) -> Callable[[State], bool]:
    """Compile a DSL expression into a predicate: State -> bool."""

    tokens = _Tokenizer(expression).tokenize()
    ast = _Parser(tokens).parse()

    def predicate(state: State) -> bool:
        return bool(_evaluate(ast, state.data or {}))

    return predicate


def _evaluate(node: Any, data: dict[str, Any]) -> Any:
    if isinstance(node, Literal):
        return node.value

    if isinstance(node, Identifier):
        return data.get(node.name)

    if isinstance(node, UnaryOp):
        if node.op == "NOT":
            return not bool(_evaluate(node.operand, data))
        raise ConstraintDSLError(f"Unsupported unary operator: {node.op}")

    if isinstance(node, BinaryOp):
        if node.op in {"AND", "OR"}:
            left = bool(_evaluate(node.left, data))
            if node.op == "AND":
                return left and bool(_evaluate(node.right, data))
            return left or bool(_evaluate(node.right, data))

        left_val = _evaluate(node.left, data)
        right_val = _evaluate(node.right, data)
        return _compare(node.op, left_val, right_val)

    raise ConstraintDSLError(f"Unknown AST node: {type(node).__name__}")


def _compare(op: str, left: Any, right: Any) -> bool:
    if op == "==":
        return left == right
    if op == "!=":
        return left != right
    if op == "<":
        return _ordered_compare(lambda a, b: a < b, left, right, op)
    if op == "<=":
        return _ordered_compare(lambda a, b: a <= b, left, right, op)
    if op == ">":
        return _ordered_compare(lambda a, b: a > b, left, right, op)
    if op == ">=":
        return _ordered_compare(lambda a, b: a >= b, left, right, op)
    raise ConstraintDSLError(f"Unsupported comparison operator: {op}")


def _ordered_compare(fn: Callable[[Any, Any], bool], left: Any, right: Any, op: str) -> bool:
    try:
        return bool(fn(left, right))
    except TypeError as exc:
        raise ConstraintDSLError(f"Cannot compare values with operator {op}: {left!r}, {right!r}") from exc
