import zebv.parsing

import pytest


def simplify(e, exp):
    return e.simplify(parsing.build_expression(parsing.tokenize(exp)))


def tokenize(exp):
    return parsing.build_expression(parsing.tokenize(x))


def test_add(e):
    assert simplify(e, "ap ap add 1 2") == tokenize("3")
    assert simplify(e, "ap ap add 2 1") == tokenize("3")
    assert simplify(e, "ap ap add 0 1") == tokenize("1")
    assert simplify(e, "ap ap add 2 3") == tokenize("5")
    assert simplify(e, "ap ap add 3 5") == tokenize("8")


def test_inc(e):
    assert simplify(e, "ap inc 0") == tokenize("1")
    assert simplify(e, "ap inc 1") == tokenize("2")
    assert simplify(e, "ap inc 2") == tokenize("3")
    assert simplify(e, "ap inc 3") == tokenize("4")
    assert simplify(e, "ap inc 300") == tokenize("301")
    assert simplify(e, "ap inc 301") == tokenize("302")
    assert simplify(e, "ap inc -1") == tokenize("0")
    assert simplify(e, "ap inc -2") == tokenize("-1")
    assert simplify(e, "ap inc -3") == tokenize("-2")
