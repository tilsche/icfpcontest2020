import re
from typing import Iterable, Iterator, Union

from . import node
from .operators import operators


class Token:
    pass


class IntLiteral(Token):
    def __init__(self, tok: str):
        self.value = int(tok)

    def __repr__(self):
        return f"IntLiteral({self.value})"

    def __str__(self):
        return f"{self.value}"


class ColonName(Token):
    def __init__(self, tok: str):
        self._id = int(tok[1:])

    def __repr__(self):
        return f"ColonName(:{self._id})"

    def __str__(self):
        return f":{self._id}"


class Literal(Token):
    def __init__(self, tok: str):
        if tok == "vec":
            tok = "cons"
        self.name = tok

    def __repr__(self):
        return f"Literal({self.name})"

    def __str__(self):
        return f"{self.name}"


class MatchPattern(Token):
    def __str__(self):
        return "="

    def __eq__(self, other):
        return isinstance(other, MatchPattern)


class Expr:
    pass


class Ap(Expr):
    def __init__(self, fst, snd):
        self.fst = fst
        self.snd = snd

    def __str__(self):
        return f"Ap({self.fst}, {self.snd})"


class Atom(Expr):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return f"Atom({self.value})"

    def to_dict(self):
        return self.__str__()


def tokenize(input: str):
    for token in input.split():
        if token.startswith(":"):
            yield ColonName(token)
        elif token == "=":
            yield MatchPattern()
        else:
            try:
                yield IntLiteral(token)
            except ValueError:
                yield Literal(token)


def _build_expression(tokens: Iterator[Token]):
    tok = next(tokens)

    if isinstance(tok, Literal):
        if tok.name == "ap":
            return node.Ap(_build_expression(tokens), _build_expression(tokens))

        if tok.name in ["?", "=", "=="]:
            raise ValueError(f"strange token {tok}")

        m = re.match(r"x(\d+)", tok.name)
        if m:
            return node.Placeholder(int(m[1]))

        if tok.name in operators:
            return operators[tok.name]

        # Assume operator
        return node.GenericOperator(tok.name)

    if isinstance(tok, ColonName):
        return node.Name(tok._id)

    if isinstance(tok, IntLiteral):
        return node.Integer(tok.value)

    raise TypeError(f"unknown token type: {type(tok)} {tok}")


def build_expression(tokens: Union[Iterable[Token], str]):
    if isinstance(tokens, str):
        tokens = tokenize(tokens)
    it = iter(tokens)
    expression = _build_expression(it)
    rest = list(it)
    if rest:
        raise RuntimeError(f"Tokens not all consumed: {rest}")
    return expression