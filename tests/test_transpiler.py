import pytest

from zebv.expression import build_expression
from zebv.transpile import Transpiler, PRELUDE
from zebv.logging import get_logger

logger = get_logger(__name__)


@pytest.fixture
def transpiler():
    yield Transpiler()


@pytest.mark.parametrize(
    "expr, transpiled",
    [
        ("ap a b", "(a b)"),
        ("ap ap cons 1 nil", "((cons 1) nil)"),
        ("1", "1"),
        (
            "ap ap s ap ap c ap eq 0 1 ap ap b ap mul 2 ap ap b pwr2 ap add -1",
            "((s (c ((eq 0) 1))) ((b (mul 2)) ((b pwr2) (add -1))))",
        ),
    ],
)
def test_transpiler(caplog, transpiler, expr, transpiled):
    # """ checkerboard = ap ap s ap ap b s ap ap c ap ap b c ap ap b ap c ap c ap ap s ap ap b s ap ap b ap b ap ap s i i lt eq ap ap s mul i nil ap ap s ap ap b s ap ap b ap b cons ap ap s ap ap b s ap ap b ap b cons ap c div ap c ap ap s ap ap b b ap ap c ap ap b b add neg ap ap b ap s mul div ap ap c ap ap b b checkerboard ap ap c add 2"""
    with caplog.at_level("DEBUG"):
        expr = build_expression(expr)
        logger.debug(f"{expr!r}")
        assert False
        assert transpiled == transpiler.transpile_expr(expr)


def test_transpile_program(caplog):
    with caplog.at_level("DEBUG"):
        pass
