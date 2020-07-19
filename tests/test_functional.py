import pytest
from zebv.expression import build_expression


def t(exp):
    return build_expression(exp)


def s(e, exp):
    return e.eval(t(exp))


def test_ap(e):
    assert s(e, "ap inc ap inc 0") == t("2")
    assert s(e, "ap inc ap inc ap inc 0") == t("3")
    # TODO
    # assert s(e, "ap inc ap dec x0") == t("x0")
    # assert s(e, "ap dec ap inc x0") == t("x0")
    # assert s(e, "ap dec ap ap add x0 1") == t("x0")
    assert s(e, "ap ap add ap ap add 2 3 4") == t("9")
    assert s(e, "ap ap add 2 ap ap add 3 4") == t("9")
    assert s(e, "ap ap add ap ap mul 2 3 4") == t("10")
    assert s(e, "ap ap mul 2 ap ap add 3 4") == t("14")


def test_s(e):
    assert s(e, "ap ap ap s add inc 1") == t("3")
    assert s(e, "ap ap ap s mul ap add 1 6") == t("42")


def test_c(e):
    assert s(e, "ap ap ap c add 1 2") == t("3")


def test_true(e):
    assert s(e, "ap ap t 1 5") == t("1")
    assert s(e, "ap ap t t i") == t("t")
    assert s(e, "ap ap t t ap inc 5") == t("t")
    assert s(e, "ap ap t ap inc 5 t") == t("6")


def test_i(e):
    assert s(e, "ap i 1") == t("1")
    assert s(e, "ap i i") == t("i")
    assert s(e, "ap i add") == t("add")
    assert s(e, "ap i ap add 1") == t("ap add 1")
