import pytest
import zebv.parsing as parsing


def t(exp):
    return parsing.build_expression(parsing.tokenize(exp))


def s(e, exp):
    return e.simplify(t(exp))


def test_add(e):
    assert s(e, "ap ap add 1 2") == t("3")
    assert s(e, "ap ap add 2 1") == t("3")
    assert s(e, "ap ap add 0 1") == t("1")
    assert s(e, "ap ap add 2 3") == t("5")
    assert s(e, "ap ap add 3 5") == t("8")


def test_inc(e):
    assert s(e, "ap inc 0") == t("1")
    assert s(e, "ap inc 1") == t("2")
    assert s(e, "ap inc 2") == t("3")
    assert s(e, "ap inc 3") == t("4")
    assert s(e, "ap inc 300") == t("301")
    assert s(e, "ap inc 301") == t("302")
    assert s(e, "ap inc -1") == t("0")
    assert s(e, "ap inc -2") == t("-1")
    assert s(e, "ap inc -3") == t("-2")


def test_dec(e):
    assert s(e, "ap dec 1") == t("0")
    assert s(e, "ap dec 2") == t("1")
    assert s(e, "ap dec 3") == t("2")
    assert s(e, "ap dec 4") == t("3")
    assert s(e, "ap dec 1024") == t("1023")
    assert s(e, "ap dec 0") == t("-1")
    assert s(e, "ap dec -1") == t("-2")
    assert s(e, "ap dec -2") == t("-3")


def test_mul(e):

    assert s(e, "ap ap mul 4 2") == t("8")
    assert s(e, "ap ap mul 3 4") == t("12")
    assert s(e, "ap ap mul 3 -2") == t("-6")
    # TODO
    # assert s(e, "ap ap mul x0 x1") == t("ap ap mul x1 x0")
    # assert s(e, "ap ap mul x0 0") == t("0")
    # assert s(e, "ap ap mul x0 1") == t("x0")


def test_div(e):
    assert s(e, "ap ap div 4 2") == t("2")
    assert s(e, "ap ap div 4 3") == t("1")
    assert s(e, "ap ap div 4 4") == t("1")
    assert s(e, "ap ap div 4 5") == t("0")
    assert s(e, "ap ap div 5 2") == t("2")
    assert s(e, "ap ap div 6 -2") == t("-3")
    assert s(e, "ap ap div 5 -3") == t("-1")
    assert s(e, "ap ap div -5 3") == t("-1")
    assert s(e, "ap ap div -5 -3") == t("1")
    # TODO
    # assert s(e, "ap ap div x0 1") == t("x0")
