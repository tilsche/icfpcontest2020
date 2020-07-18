from zebv.eval import Evaluator
from zebv.node import Number
from zebv.parsing import build_expression, tokenize

e = Evaluator()


def tt(s):
    print(list(e.simplify_once(build_expression(tokenize(s)))))


# tt("ap ap ap s mul ap add 1 6")
# tt("ap foo ap ap mul 2 3")
# tt("ap pwr2 0")
# tt("ap ap ap s ap ap c ap eq 0 1 ap ap b ap mul 2 ap ap b pwr2 ap add -1 0")

print(e.simplify(build_expression(tokenize("ap pwr2 20")), (Number,)))
