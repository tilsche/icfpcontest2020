from zebv.eval import Evaluator
from zebv.parsing import build_expression, tokenize

import pytest


@pytest.fixture
def e():
    yield Evaluator()
