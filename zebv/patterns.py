import itertools

from . import parsing
from .node import Name, Operator


def parse_patterns(text: str):
    token_lists = [
        parsing.tokenize(line) for line in text.splitlines() if not line.startswith("#")
    ]
    shrink_patterns = []
    expand_patterns = []
    direct_patterns = {}
    for tokens in token_lists:
        left, right = [
            list(group)
            for k, group in itertools.groupby(
                tokens, lambda x: x == parsing.MatchPattern()
            )
            if not k
        ]
        ex_left = parsing.build_expression(left)
        ex_right = parsing.build_expression(right)
        if not ex_left.children:
            assert isinstance(ex_left, (Operator, Name))
            assert ex_left not in direct_patterns
            direct_patterns[ex_left] = ex_right
        elif len(ex_left) > len(ex_right):
            shrink_patterns.append((ex_left, ex_right))
        else:
            expand_patterns.append((ex_left, ex_right))
    return shrink_patterns, expand_patterns, direct_patterns


_default_pattern_str = """
ap ap ap s x0 x1 x2   =   ap ap x0 x2 ap x1 x2
# ap ap ap c x0 x1 x2   =   ap ap x0 x2 x1
# ap ap ap b x0 x1 x2   =   ap x0 ap x1 x2
# ap ap t x0 x1   =   x0
# ap ap f x0 x1   =   x1
pwr2   =   ap ap s ap ap c ap eq 0 1 ap ap b ap mul 2 ap ap b pwr2 ap add -1
# ap i x0   =   x0
ap ap ap cons x0 x1 x2   =   ap ap x2 x0 x1
ap car ap ap cons x0 x1   =   x0
ap cdr ap ap cons x0 x1   =   x1
# ap nil x0   =   t
# ap isnil nil   =   t
# ap isnil ap ap cons x0 x1   =   f
#vec   =   cons
# ap ap ap if0 0 x0 x1   =   x0
# ap ap ap if0 1 x0 x1   =   x1
# ap modem x0 = ap dem ap mod x0
# ap modem x0 = x0
# ap ap f38 x2 x0 = ap ap ap if0 ap car x0 ap ap cons ap modem ap car ap cdr x0 ap ap cons ap multipledraw ap car ap cdr ap cdr x0 nil ap ap ap interact x2 ap modem ap car ap cdr x0 ap send ap car ap cdr ap cdr x0
# ap ap ap interact x2 x4 x3 = ap ap f38 x2 ap ap x2 x4 x3
checkerboard = ap ap s ap ap b s ap ap c ap ap b c ap ap b ap c ap c ap ap s ap ap b s ap ap b ap b ap ap s i i lt eq ap ap s mul i nil ap ap s ap ap b s ap ap b ap b cons ap ap s ap ap b s ap ap b ap b cons ap c div ap c ap ap s ap ap b b ap ap c ap ap b b add neg ap ap b ap s mul div ap ap c ap ap b b checkerboard ap ap c add 2
""".strip()

pattern_operators = (
    # "s",
    # "c",
    # "b",
    # "t",
    # "f",
    "pwr2",
    # "i",
    "cons",
    "car",
    "cdr",
    # "nil",
    # "isnil",
    # "vec",
    # "if0",
    # "modem",
    # "f38",
    # "interact",
    "checkerboard",
)

(
    default_shrink_patterns,
    default_expand_patterns,
    default_direct_patterns,
) = parse_patterns(_default_pattern_str)
