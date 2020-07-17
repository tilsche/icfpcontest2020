from typing import Iterable


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

    def to_dict(self):
        return {}

    def ev(self) -> "Expr":
        return self


class Ap(Expr):
    def __init__(self, fst, snd):
        self.fst = fst
        self.snd = snd

    def __str__(self):
        return f"Ap({self.fst}, {self.snd})"

    def to_dict(self):
        return self.fst.to_dict(), self.snd.to_dict()

    def ev(self):
        if isinstance(self.fst, Atom):
            KNOWN = {
                0b100001011: lambda x: x + 1,
                "inc": lambda x: x + 1,
            }
            return KNOWN[self.fst.value](self.snd.value)
        else:
            return self


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
