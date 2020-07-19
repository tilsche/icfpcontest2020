import click
import click_log

from .expression import Ap, Expression, Operator, build_expression

from .logging import get_logger

logger = get_logger(__name__)

PRELUDE_CHEATING = {
    "ap": r"(\f a -> f a)",
    "inc": r"(\x -> x + (1 :: Int))",
    "dec": r"(\x -> x + (-1 :: Int))",
    "add": "(+)",
    "mul": "(*)",
    "neg": "negate",
    ##
    # already defined "div": "div",
    "eq": r"((==) :: Int -> Int -> Bool)",
    "lt": r"((<) :: Int -> Int -> Bool)",
    # "eq": r"(\x y -> if (x :: Int) == y then t else f)",
    # "lt": r"(\x y -> if (x :: Int) < y then t else f)",
    ##
    "s": r"(\x y z -> (x z) (y z))",
    "c": r"(\x y z -> (x z) y)",
    "b": r"(\x y z -> x (y z))",
    "t": r"(\x y -> x)",
    "f": r"(\x y -> y)",
    "i": "id",
    ##
    # "nil": r"[]",
    # "cons": r"cons",  # r"\x y -> [x, y]",
    # "car": r"head",
    # "cdr": r"tail",
    "nil": r"[]",
    "cons": r"(\x y -> x : y)",
    "car": r"(\x -> case x of {[] -> []; (x:_) -> x})",
    "cdr": r"(\x -> case x of {[] -> []; (_:xs) -> xs})",
    "isnil": r"(\x -> case x of {[] -> True; (_:_) -> False})",
    "vec": "cons",
    ##
    "mod": "undefined :: d -> m",
    "demod": "undefined :: m -> d",
    "send": "undefined",
    "draw": "undefined",
}

PRELUDE = {
    "ap": r"(\f a -> f a)",
    "inc": r"(\x -> x + (1 :: Int))",
    "dec": r"(\x -> x + (-1 :: Int))",
    "add": "(+)",
    "mul": "(*)",
    "neg": "negate",
    ##
    # already defined "div": "div",
    # "eq": "((==) :: Int -> Int -> Bool)",
    # "lt": "((<) :: Int -> Int -> Bool)",
    "eq": r"(\x y -> if (x :: Int) == y then t else f)",
    "lt": r"(\x y -> if (x :: Int) < y then t else f)",
    ##
    "s": r"(\x y z -> (x z) (y z))",
    "c": r"(\x y z -> (x z) y)",
    "b": r"(\x y z -> x (y z))",
    "t": r"(\x y -> x)",
    "f": r"(\x y -> y)",
    "i": "id",
    ##
    "nil": r"(\_ -> t)",
    "cons": r"(\x y z -> z x y)",
    "car": r"(\x -> x t)",
    "cdr": r"(\x -> x f)",
    "isnil": r"(\l x y -> undefined)",
    "vec": "cons",
    ##
    "mod": "undefined :: d -> m",
    "demod": "undefined :: m -> d",
    "send": "undefined",
    "draw": "undefined",
}


class Transpiler:
    def transpile(self, name, expression) -> str:
        expression = build_expression(expression.strip())
        return f"{self.make_identifier(name)} = {self.transpile_expr(expression)}"

    def make_identifier(self, name: str) -> str:
        return name.strip().replace(":", "_")

    def make_int_literal(self, lit: int) -> str:
        return f"({lit} :: Int)"

    def transpile_expr(self, expression: Expression) -> str:
        # string, integer or ap
        if isinstance(expression, Ap):
            logger.debug(f"Parsing Ap: {expression!r}")
            op = self.transpile_expr(expression.op)
            arg = self.transpile_expr(expression.arg)
            return f"({op} {arg})"
        elif isinstance(expression, Operator):
            logger.debug(f"Parsing Operator: {expression!r}")
            try:
                num = int(expression)
                return self.make_int_literal(num)
            except Exception:
                return self.make_identifier(expression)
        elif isinstance(expression, int):
            return self.make_int_literal(expression)
        else:
            raise ValueError(
                f"The fuck is this? ({expression}, type={type(expression)})"
            )

    def transpile_program(self, program: str, prelude=PRELUDE_CHEATING) -> str:
        defs = [f"{name} = {expr}" for name, expr in prelude.items()]

        defs.append("\n-- PRELUDE END --\n")

        for definition in program.splitlines():
            if definition.startswith("#"):
                continue

            name, expr = definition.split("=")
            defs.append(self.transpile(name, expr))

        return "\n".join(defs)


@click.command()
@click.argument("program", type=click.File("r"))
@click_log.simple_verbosity_option(logger)
def transpile(program):
    import sys

    sys.setrecursionlimit(5000)

    program = program.read()
    print(Transpiler().transpile_program(program))
