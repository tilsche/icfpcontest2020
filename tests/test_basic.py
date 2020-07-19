from zebv.eval import Evaluator
from zebv.expression import build_expression

e = Evaluator()


def tt(s):
    print(list(e.simplify_once(build_expression(s))))


# tt("ap ap ap s mul ap add 1 6")
# tt("ap foo ap ap mul 2 3")
# tt("ap pwr2 0")
# tt("ap ap ap s ap ap c ap eq 0 1 ap ap b ap mul 2 ap ap b pwr2 ap add -1 0")

print(e.eval(build_expression("ap pwr2 20")))
