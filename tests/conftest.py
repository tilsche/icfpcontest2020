import pytest
from zebv.eval import Evaluator
from zebv.parsing import build_expression, tokenize


@pytest.fixture
def e():
    yield Evaluator()


@pytest.fixture
def simplify(e):
    yield lambda x: e.simplify(build_expression(tokenize(x)))


@pytest.fixture
def tokenize(e):
    yield lambda x: build_expression(tokenize(x))
