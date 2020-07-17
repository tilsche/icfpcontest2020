import pytest


def test_add(simplify, tokenize):
    assert simplify("ap ap add 1 2") == tokenize("3")
    assert simplify("ap ap add 2 1") == tokenize("3")
    assert simplify("ap ap add 0 1") == tokenize("1")
    assert simplify("ap ap add 2 3") == tokenize("5")
    assert simplify("ap ap add 3 5") == tokenize("8")


def test_inc(simplify, tokenize):
    assert simlpify("ap inc 0") == tokenize("1")
    assert simlpify("ap inc 1") == tokenize("2")
    assert simlpify("ap inc 2") == tokenize("3")
    assert simlpify("ap inc 3") == tokenize("4")
    assert simlpify("ap inc 300") == tokenize("301")
    assert simlpify("ap inc 301") == tokenize("302")
    assert simlpify("ap inc -1") == tokenize("0")
    assert simlpify("ap inc -2") == tokenize("-1")
    assert simlpify("ap inc -3") == tokenize("-2")
