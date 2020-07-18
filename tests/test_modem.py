import pytest
from zebv.modem import demod, mod, mod_num, mod_node, _to_tuple_list
from zebv.operators import Number, Nil, Cons
from zebv.node import Ap

TEST_NODES = [
    (Number(0), 0, "010"),
    (Number(1), 1, "01100001"),
    (Nil(), (), "00"),
    (Ap(Ap(Cons(), Nil()), Nil()), ((), ()), "110000"),
    (Ap(Ap(Cons(), Number(0)), Nil()), (0, ()), "1101000"),
    (Ap(Ap(Cons(), Number(1)), Number(2)), (1, 2), "110110000101100010"),
    (
        Ap(Ap(Cons(), Number(1)), Ap(Ap(Cons(), Number(2)), Nil())),
        (1, (2, ())),
        "1101100001110110001000",
    ),
]


@pytest.mark.parametrize(
    "input, expected", [(input, expected) for (_, expected, input) in TEST_NODES]
)
def test_demod(input, expected):
    assert demod(input) == expected


@pytest.mark.parametrize(
    "input, expected",
    [(tuple_list, expected) for (_, tuple_list, expected) in TEST_NODES],
)
def test_mod(input, expected):
    assert mod(input) == expected


@pytest.mark.parametrize(
    "node, tuple_list", [(node, tuple_list) for (node, tuple_list, _) in TEST_NODES],
)
def test_to_tuple_list(node, tuple_list):
    assert _to_tuple_list(node) == tuple_list


@pytest.mark.parametrize(
    "node, expected", [(node, expected) for (node, _, expected) in TEST_NODES],
)
def test_mod_node(node, expected):
    assert mod_node(node) == expected


TEST_NUMBERS = [
    (0, "010"),
    (1, "01100001"),
    (-1, "10100001"),
    (2, "01100010"),
    (-2, "10100010"),
    (15, "01101111"),
    (-15, "10101111"),
    (16, "0111000010000"),
    (-16, "1011000010000"),
    (255, "0111011111111"),
    (-255, "1011011111111"),
    (256, "011110000100000000"),
    (-256, "101110000100000000"),
]


@pytest.mark.parametrize("input, expected", TEST_NUMBERS)
def test_mod_num(caplog, input, expected):
    with caplog.at_level("DEBUG"):
        assert mod_num(input) == expected


@pytest.mark.parametrize(
    "number_node, expected", [(Number(n), expected) for n, expected in TEST_NUMBERS]
)
def test_mod_node_number(number_node, expected):
    assert mod_node(number_node) == expected
