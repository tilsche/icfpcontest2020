from zebv import patterns
from zebv.eval import Evaluator
from zebv.node import Ap, Integer
from zebv.operators import Cons, Nil
from zebv.parsing import build_expression, tokenize

e = Evaluator()


print(
    e.simplify(
        build_expression(tokenize("ap ap checkerboard 4 0")), (Cons, Nil, Ap, Integer)
    ).sugar
)
