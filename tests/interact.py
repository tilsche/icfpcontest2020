from zebv import patterns
from zebv.eval import Evaluator
from zebv.interact import Interaction
from zebv.node import Ap, Number
from zebv.operators import Cons, Nil
from zebv.parsing import build_expression, tokenize
from zebv.patterns import parse_patterns

data = """
statefuldraw = ap ap b ap b ap ap s ap ap b ap b ap cons 0 ap ap c ap ap b b cons ap ap c cons nil ap ap c cons nil ap c cons
""".strip()

i = Interaction(data, "statefuldraw")
i(4, 8)
i(7, 7)
i(12, 14)
