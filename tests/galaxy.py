from zebv import patterns
from zebv.eval import Evaluator
from zebv.node import Ap, Number
from zebv.operators import Cons, Nil
from zebv.parsing import build_expression, tokenize
from zebv.patterns import parse_patterns

print(patterns.default_patterns)

extra_patterns = parse_patterns(
    """
statelessdraw = ap ap c ap ap b b ap ap b ap b ap cons 0 ap ap c ap ap b b cons ap ap c cons nil ap ap c ap ap b cons ap ap c cons nil nil
""".strip()
)

e = Evaluator(extra_patterns)

l = e.simplify(
    # build_expression(tokenize("ap ap statelessdraw nil ap ap cons 3 7"))
    build_expression(tokenize("ap ap ap interact statelessdraw nil ap ap vec 3 7")),
    (Ap, Cons, Nil, Number, "multipledraw"),
).sugar
print(l)
