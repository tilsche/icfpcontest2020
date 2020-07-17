import requests
import sys
import pprint
from logging import getLogger
from typing import Iterable

logger = getLogger(__name__)

import click, numpy, scipy, pandas

print("click", click.__version__)
print("np", numpy.__version__)
print("scipy", scipy.__version__)
print("pandas", pandas.__version__)


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
        return (self.fst.to_dict(), self.snd.to_dict())

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


def tokenize(input: Iterable[str]):
    for token in input:
        if token.startswith(":"):
            yield ColonName(token)
        else:
            try:
                yield IntLiteral(token)
            except ValueError:
                yield Literal(token)


def parse(toks: Iterable[str]):
    tok = next(toks)
    if (isinstance(tok, ColonName) and tok._id == 0) or (
        isinstance(tok, Literal) and tok.name == "ap"
    ):
        fst = parse(toks)
        snd = parse(toks)
        return Ap(fst, snd)
    else:
        return Atom(tok)


def main():
    PROGRAM = "ap ap s ap ap c ap eq 0 1 ap ap b ap mul 2 ap ap b pwr2 ap add -1"
    # PROGRAM = "ap ap ap s x0 x1 x2"
    # PROGRAM = ":0 ap add 0 x0"

    tokens = list(tokenize(PROGRAM.split()))
    print(" ".join(map(repr, tokens)))

    tree = parse(tok for tok in tokens)
    print(str(tree))

    print(Ap(Atom(0b100001011), Atom(1)).ev())
    print(Ap(Atom("inc"), Atom(1)).ev())

    # server_url = sys.argv[1]
    # player_key = sys.argv[2]
    # print("ServerUrl: %s; PlayerKey: %s" % (server_url, player_key))

    # res = requests.post(server_url, data=player_key)
    # if res.status_code != 200:
    #     print("Unexpected server response:")
    #     print("HTTP code:", res.status_code)
    #     print("Response body:", res.text)
    #     exit(2)
    # print("Server response:", res.text)


if __name__ == "__main__":
    main()
