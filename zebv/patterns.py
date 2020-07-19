from .expression import Operator, build_expression

_default_function_str = """
pwr2 = ap ap s ap ap c ap eq 0 1 ap ap b ap mul 2 ap ap b pwr2 ap add -1
checkerboard = ap ap s ap ap b s ap ap c ap ap b c ap ap b ap c ap c ap ap s ap ap b s ap ap b ap b ap ap s i i lt eq ap ap s mul i nil ap ap s ap ap b s ap ap b ap b cons ap ap s ap ap b s ap ap b ap b cons ap c div ap c ap ap s ap ap b b ap ap c ap ap b b add neg ap ap b ap s mul div ap ap c ap ap b b checkerboard ap ap c add 2
"""


def parse_function(line):
    f, definition = line.split("=")
    f = build_expression(f)
    assert isinstance(f, Operator)
    return f, build_expression(definition)


def parse_functions(text):
    return dict(parse_function(line) for line in text.strip().splitlines())


default_functions = parse_functions(_default_function_str)
