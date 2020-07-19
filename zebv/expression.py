from sys import intern
from typing import Generator, Iterable, Iterator, Optional, Tuple, Union

Operator = str
# TODO Placeholder, Function ?
Integer = int
Literal = Union[Operator, Integer]

Expression = Union["Ap", Literal]


class Ap:
    _evaluated: Optional[Expression] = None
    _op: Expression
    _arg: Expression

    def __init__(self, op: Expression, arg: Expression):
        self._op = op
        self._arg = arg

    @property
    def evaluated(self):
        return self._evaluated

    @evaluated.setter
    def evaluated(self, value):
        assert not self._evaluated
        self._evaluated = value

    @property
    def op(self):
        return self._op

    @property
    def arg(self):
        return self._arg

    def __eq__(self, other):
        return (
            isinstance(other, Ap) and self._arg == other._arg and self._op == other._op
        )

    def __repr__(self):
        return f"(ap {self.op!r} {self.arg!r})"

    def __str__(self):
        return f"ap {self.op} {self.arg}"


Token = Union[int, str]


def _tokenize_expression(input: str) -> Generator[Token, None, None]:
    for token in input.split():
        try:
            yield int(token)
        except ValueError:
            if token == "vec":
                token = "cons"
            yield intern(token)


def _build_expression(tokens: Iterator[Token]) -> Expression:
    tok = next(tokens)

    if tok == "ap":
        return Ap(_build_expression(tokens), _build_expression(tokens))

    if tok in ("?", "=", "=="):
        raise ValueError(f"strange token {tok}")

    # todo confirm it is only a placeholder (:123), variable (x123), or known operator
    return tok


def build_expression(tokens: Union[Iterable[Token], str]) -> Expression:
    if isinstance(tokens, str):
        tokens = _tokenize_expression(tokens)
    it = iter(tokens)
    expression = _build_expression(it)
    rest = list(it)
    if rest:
        raise RuntimeError(f"Tokens not all consumed: {rest}")
    return expression


def as_list(expression: Expression) -> Tuple[Expression]:
    if expression == "nil":
        return []
    assert isinstance(expression, Ap)
    assert isinstance(expression.op, Ap)
    assert expression.op.op == "cons"
    return (expression.op.arg, *as_list(expression.arg))


def as_vector(expression: Expression) -> Tuple[Expression]:
    assert isinstance(expression, Ap)
    assert isinstance(expression.op, Ap)
    assert expression.op.op == "cons"
    return expression.op.arg, expression.arg
