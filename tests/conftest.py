import pytest
from zebv.eval import Evaluator
from zebv.parsing import build_expression, tokenize


@pytest.fixture
def e():
    yield Evaluator()
