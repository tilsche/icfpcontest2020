from .expression import Ap, Expression, Integer, Literal, Operator, build_expression
from .patterns import default_functions, parse_functions


class Evaluator:
    def __init__(self, context=""):
        self._functions = default_functions
        self._functions.update(parse_functions(context))

    def eval(self, expression: Expression) -> Expression:
        if isinstance(expression, Ap) and expression.evaluated is not None:
            return expression.evaluated
        initial_node = expression
        while True:
            result = self._try_eval(expression)
            if result == expression:
                if isinstance(initial_node, Ap):
                    initial_node.evaluated = result
                else:
                    print(initial_node, result)
                return result
            expression = result

    def _try_eval(self, expression: Expression) -> Expression:
        if isinstance(expression, Ap) and expression.evaluated is not None:
            return expression.evaluated

        if isinstance(expression, Operator):
            try:
                return self._functions[expression]
            except KeyError:
                pass
        if isinstance(expression, Ap):
            fun1 = self.eval(expression.op)
            x = expression.arg

            if isinstance(fun1, Operator):
                if fun1 == "neg":
                    xn = self.eval(x)
                    assert isinstance(xn, Integer)
                    return -xn
                elif fun1 == "i":
                    return x
                elif fun1 == "nil":
                    return "t"
                elif fun1 == "isnil":
                    return Ap(x, Ap("t", Ap("t", "f")))
                elif fun1 == "car":
                    return Ap(x, "t")
                elif fun1 == "cdr":
                    return Ap(x, "f")

            elif isinstance(fun1, Ap):
                fun2 = self.eval(fun1.op)
                y = fun1.arg
                if isinstance(fun2, Operator):
                    if fun2 == "t":
                        return y
                    if fun2 == "f":
                        return x
                    if fun2 in ("add", "mul", "div", "lt", "eq"):
                        xn = self.eval(x)
                        assert isinstance(xn, Integer)
                        yn = self.eval(y)
                        assert isinstance(yn, Integer)
                        if fun2 == "add":
                            return xn + yn
                        if fun2 == "mul":
                            return xn * yn
                        if fun2 == "div":
                            return int(yn / xn)
                        if fun2 == "lt":
                            return "t" if yn < xn else "f"
                        if fun2 == "eq":
                            return "t" if xn == yn else "f"
                        raise RuntimeError(fun2)

                    if fun2 == "cons":
                        return self._eval_cons(y, x)
                if isinstance(fun2, Ap):
                    fun3 = self.eval(fun2.op)
                    z = fun2.arg
                    if isinstance(fun3, Operator):
                        if fun3 == "s":
                            return Ap(Ap(z, x), Ap(y, x))
                        elif fun3 == "c":
                            return Ap(Ap(z, x), y)
                        elif fun3 == "b":
                            return Ap(z, Ap(y, x))
                        elif fun3 == "cons":
                            return Ap(Ap(x, z), y)
        return expression

    def _eval_cons(self, a: Expression, b: Expression):
        res = Ap(Ap("cons", self.eval(a)), self.eval(b))
        res.evaluated = res
        return res
