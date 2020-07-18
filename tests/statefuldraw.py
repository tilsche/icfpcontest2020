from zebv.eval import Evaluator
from zebv.node import Ap, Number
from zebv.operators import Cons, Nil
from zebv.parsing import build_expression, tokenize
from zebv.patterns import parse_patterns


def test_parse_eval_and_simplify(statefuldraw):
    extra_patterns = parse_patterns(statefuldraw)

    e = Evaluator(*extra_patterns)

    simplified = e.simplify(
        # build_expression(tokenize("ap ap statelessdraw nil ap ap cons 3 7"))
        build_expression(tokenize("ap ap ap interact statefuldraw nil ap ap vec 0 0")),
        (Ap, Cons, Nil, Number, "multipledraw"),
    ).sugar
    print(simplified)
