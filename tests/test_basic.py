from zebv import patterns
from zebv.eval import Evaluator
from zebv.node import build_expression
from zebv.parsing import tokenize

print(patterns.default_patterns)

e = Evaluator()
print(list(e.simplify_once(build_expression(tokenize("ap ap ap s mul ap add 1 6")))))
