from zebv import patterns
from zebv.eval import Evaluator
from zebv.node import Ap, Number
from zebv.operators import Cons, Nil
from zebv.parsing import build_expression, tokenize
from zebv.patterns import parse_patterns

extra_patterns = parse_patterns(
    """
statefuldraw = ap ap b ap b ap ap s ap ap b ap b ap cons 0 ap ap c ap ap b b cons ap ap c cons nil ap ap c cons nil ap c cons
""".strip()
)

e = Evaluator(*extra_patterns)

l = e.simplify(
    # build_expression(tokenize("ap ap statelessdraw nil ap ap cons 3 7"))
    build_expression(tokenize("ap ap ap interact statefuldraw nil ap ap vec 0 0")),
    (Ap, Cons, Nil, Number, "multipledraw"),
).sugar
print(l)
