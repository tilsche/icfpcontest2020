from zebv import patterns
from zebv.eval import Evaluator
from zebv.parsing import build_expression, tokenize

print(patterns.default_patterns)

e = Evaluator()
print(list(e.simplify_once(build_expression(tokenize("ap ap ap s mul ap add 1 6")))))
