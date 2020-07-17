import pytest
from zebv.modem import demod, mod, mod_num

MODULATED_TO_DEMODULATED = [
    ("010", 0),
    ("01100001", 1),
    ("00", ()),
    ("110000", ((), ())),
    ("1101000", (0, ())),
    ("110110000101100010", (1, 2)),
    ("1101100001110110001000", (1, (2, ()))),
]


@pytest.mark.parametrize("input, expected", MODULATED_TO_DEMODULATED)
def test_demod(input, expected):
    assert demod(input) == expected


@pytest.mark.parametrize(
    "input, expected", list(map(lambda e: (e[1], e[0]), MODULATED_TO_DEMODULATED))
)
def test_mod(input, expected):
    assert mod(input) == expected


@pytest.mark.parametrize(
    "input, expected",
    [
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
    ],
)
def test_mod_num(caplog, input, expected):
    with caplog.at_level("DEBUG"):
        assert mod_num(input) == expected
