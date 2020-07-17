from typing import Union

from .node import NoEvalError, Number, Operator, Variable

OperatorArgument = Union[Number, Variable]


class HardcodedOperator(Operator):
    name: str

    def __str__(self):
        return self.name


class Inc(HardcodedOperator):
    name = "inc"

    def __call__(self, argument: OperatorArgument):
        if isinstance(argument, Number):
            return Number(argument.value + 1)
        else:
            raise NoEvalError()


class Dec(HardcodedOperator):
    name = "dec"

    def __call__(self, argument: OperatorArgument):
        if isinstance(argument, Number):
            return Number(argument.value - 1)
        else:
            raise NoEvalError()


class Add(HardcodedOperator):
    name = "add"

    def __call__(self, a1: OperatorArgument):
        if isinstance(a1, Number):
            value1 = a1.value

            def add2(a2: OperatorArgument):
                if isinstance(a2, Number):
                    return Number(value1 + a2.value)

            return add2
        else:
            raise NoEvalError()


class Mul(HardcodedOperator):
    name = "add"

    def __call__(self, a1: OperatorArgument):
        if isinstance(a1, Number):
            value1 = a1.value

            def mul2(a2: OperatorArgument):
                if isinstance(a2, Number):
                    return Number(value1 * a2.value)

            return mul2
        else:
            raise NoEvalError()


class Div(HardcodedOperator):
    name = "add"

    def __call__(self, a1: OperatorArgument):
        if isinstance(a1, Number):
            value1 = a1.value

            def div2(a2: OperatorArgument):
                if isinstance(a2, Number):
                    return Number(value1 // a2.value)

            return div2
        else:
            raise NoEvalError()


class T(HardcodedOperator):
    name = "t"

    def __call__(self, a1: OperatorArgument):
        raise NoEvalError()


class F(HardcodedOperator):
    name = "f"

    def __call__(self, a1: OperatorArgument):
        raise NoEvalError()


class Eq(HardcodedOperator):
    name = "eq"

    def __call__(self, a1: OperatorArgument):
        def eq2(a2: OperatorArgument):
            if a1 == a2:
                return True

            if isinstance(a1, Number) and isinstance(a2, Number):
                return a1.value == a2.value

            raise NoEvalError()

        return eq2


class Lt(HardcodedOperator):
    name = "lt"

    def __call__(self, a1: OperatorArgument):
        def eq2(a2: OperatorArgument):
            if a1 == a2:
                return False

            if isinstance(a1, Number) and isinstance(a2, Number):
                return a1.value < a2.value

            raise NoEvalError()

        return eq2


operators = {op().name: op() for op in (Inc, Dec, Add, Mul, Div, T, F, Eq, Lt)}
