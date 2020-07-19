import pytest
from zebv.eval import Evaluator


@pytest.fixture
def e():
    yield Evaluator(
        """
            inc = ap add 1
            dec = ap add -1
        """
    )


@pytest.fixture
def statefuldraw():
    yield "statefuldraw = ap ap b ap b ap ap s ap ap b ap b ap cons 0 ap ap c ap ap b b cons ap ap c cons nil ap ap c cons nil ap c cons"
