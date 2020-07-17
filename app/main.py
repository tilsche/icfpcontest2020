import requests
import sys
import pprint
from logging import getLogger
from typing import Iterable

logger = getLogger(__name__)

import click, numpy, scipy, pandas


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


def demod_num(input: str) -> (int, str):
    bits = 0
    while True:
        (fst, input) = input[0], input[1:]
        if fst == "1":
            bits += 1
        else:
            break

    if not bits:
        return (0, input)
    else:
        value_len = bits * 4
        (value, rest) = input[:value_len], input[value_len:]
        return (int(value, base=2), rest)


TEST = [
    ("00", "nil"),
    ("110000", "ap ap cons nil nil"),
    ("1101000", "ap ap cons 0 nil"),
    ("110110000101100010", "ap ap cons 1 2"),
    ("1101100001110110001000", "ap ap cons 1 ap ap cons 2 nil"),
]


def demod(input: str):
    (_type, value) = (input[:2], input[2:])
    # print(f"demod: {_type=} {value=}")

    if _type == "00":
        return ("nil", value)
    elif _type == "01":
        (num, rest) = demod_num(value)
        return (1 * num, rest)
    elif _type == "10":
        (num, rest) = demod_num(value)
        return (-1 * num, rest)
    else:  # 11 == cons
        (head, tail) = demod(value)
        # print(f"{head=} {tail=}")
        (tail, rest) = demod(tail)
        # print(f"{tail=} {rest=}")
        return (f"ap ap cons {head} {tail}", rest)


def debug_demod(input):
    print(f"demod({input}) = {demod(input)}")


def main():
    for (input, expected) in TEST:
        print(f"demod({input}) = {demod(input)}")
        (computed, rest) = demod(input)
        assert computed == expected
        assert rest == ""

    debug_demod("1101100001111101100010110110001100110110010000")

    for response in (
        "110110000111011111100001001111110101000000",
        "110110000111011111100001001111110100110000",
        "110110000111011111100001001010110001110100",
    ):
        print(f"From response ({response})")
        debug_demod(response)

    return

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
