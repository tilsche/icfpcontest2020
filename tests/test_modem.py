import pytest
from zebv.expression import Ap, Integer
from zebv.modem import _to_tuple_list, demod, demod_node, mod, mod_node, mod_num

TEST_NODES = [
    (Integer(0), 0, "010"),
    (Integer(1), 1, "01100001"),
    ("nil", (), "00"),
    (Ap(Ap("cons", "nil"), "nil"), ((), ()), "110000"),
    (Ap(Ap("cons", Integer(0)), "nil"), (0, ()), "1101000"),
    (Ap(Ap("cons", Integer(1)), Integer(2)), (1, 2), "110110000101100010"),
    (
        Ap(Ap("cons", Integer(1)), Ap(Ap("cons", Integer(2)), "nil")),
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


@pytest.mark.parametrize(
    "input, node", [(input, node) for (node, _, input) in TEST_NODES]
)
def test_demod_node(input, node):
    assert demod_node(input) == node


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
    "number_node, expected", [(Integer(n), expected) for n, expected in TEST_NUMBERS]
)
def test_mod_node_number(number_node, expected):
    assert mod_node(number_node) == expected
