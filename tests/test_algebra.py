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


def test_eq(e):
    assert s(e, "ap ap eq x0 x0") == t("t")
    assert s(e, "ap ap eq 0 -2") == t("f")
    assert s(e, "ap ap eq 0 -1") == t("f")
    assert s(e, "ap ap eq 0 0") == t("t")
    assert s(e, "ap ap eq 0 1") == t("f")
    assert s(e, "ap ap eq 0 2") == t("f")
    assert s(e, "ap ap eq 1 -1") == t("f")
    assert s(e, "ap ap eq 1 0") == t("f")
    assert s(e, "ap ap eq 1 1") == t("t")
    assert s(e, "ap ap eq 1 2") == t("f")
    assert s(e, "ap ap eq 1 3") == t("f")
    assert s(e, "ap ap eq 2 0") == t("f")
    assert s(e, "ap ap eq 2 1") == t("f")
    assert s(e, "ap ap eq 2 2") == t("t")
    assert s(e, "ap ap eq 2 3") == t("f")
    assert s(e, "ap ap eq 2 4") == t("f")
    assert s(e, "ap ap eq 19 20") == t("f")
    assert s(e, "ap ap eq 20 20") == t("t")
    assert s(e, "ap ap eq 21 20") == t("f")
    assert s(e, "ap ap eq -19 -20") == t("f")
    assert s(e, "ap ap eq -20 -20") == t("t")
    assert s(e, "ap ap eq -21 -20") == t("f")


def test_lt(e):
    assert s(e, "ap ap lt 0 -1") == t("f")
    assert s(e, "ap ap lt 0 0") == t("f")
    assert s(e, "ap ap lt 0 1") == t("t")
    assert s(e, "ap ap lt 0 2") == t("t")
    assert s(e, "ap ap lt 1 0") == t("f")
    assert s(e, "ap ap lt 1 1") == t("f")
    assert s(e, "ap ap lt 1 2") == t("t")
    assert s(e, "ap ap lt 1 3") == t("t")
    assert s(e, "ap ap lt 2 1") == t("f")
    assert s(e, "ap ap lt 2 2") == t("f")
    assert s(e, "ap ap lt 2 3") == t("t")
    assert s(e, "ap ap lt 2 4") == t("t")
    assert s(e, "ap ap lt 19 20") == t("t")
    assert s(e, "ap ap lt 20 20") == t("f")
    assert s(e, "ap ap lt 21 20") == t("f")
    assert s(e, "ap ap lt -19 -20") == t("f")
    assert s(e, "ap ap lt -20 -20") == t("f")
    assert s(e, "ap ap lt -21 -20") == t("t")


def test_neg(e):
    assert s(e, "ap neg 0") == t("0")
    assert s(e, "ap neg 1") == t("-1")
    assert s(e, "ap neg -1") == t("1")
    assert s(e, "ap neg 2") == t("-2")
    assert s(e, "ap neg -2") == t("2")
