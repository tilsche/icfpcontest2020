import pytest
from zebv.eval import Evaluator
from zebv.parsing import build_expression, tokenize


@pytest.fixture
def e():
    yield Evaluator()


@pytest.fixture
def statefuldraw():
    yield "statefuldraw = ap ap b ap b ap ap s ap ap b ap b ap cons 0 ap ap c ap ap b b cons ap ap c cons nil ap ap c cons nil ap c cons"
