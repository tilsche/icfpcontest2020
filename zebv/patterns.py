import itertools

from . import parsing


def parse_patterns(text: str):
    token_lists = [parsing.tokenize(line) for line in text.splitlines()]
    patterns = []
    for tokens in token_lists:
        left, right = [
            list(group)
            for k, group in itertools.groupby(
                tokens, lambda x: x == parsing.MatchPattern()
            )
            if not k
        ]
        patterns.append(
            (parsing.build_expression(left), parsing.build_expression(right))
        )
    return patterns


_default_pattern_str = """
ap ap ap s x0 x1 x2   =   ap ap x0 x2 ap x1 x2
ap ap ap c x0 x1 x2   =   ap ap x0 x2 x1
ap ap ap b x0 x1 x2   =   ap x0 ap x1 x2
ap ap t x0 x1   =   x0
ap ap f x0 x1   =   x1
pwr2   =   ap ap s ap ap c ap eq 0 1 ap ap b ap mul 2 ap ap b pwr2 ap add -1
""".strip()

pattern_operators = "s", "c", "b", "t", "f", "pwr2"

default_patterns = parse_patterns(_default_pattern_str)
