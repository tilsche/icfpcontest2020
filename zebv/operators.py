from abc import abstractmethod
from typing import Union

from .node import NoEvalError, Number, Operator, Variable

OperatorArgument = Union[Number, Variable]


class HardcodedOperator(Operator):
    def __eq__(self, other):
        return type(other) == type(self)


class EvaluatableOperator(HardcodedOperator):
    arity: int

    @abstractmethod
    def __call__(self, *args):
        raise NoEvalError()


class UnaryOperator(EvaluatableOperator):
    arity = 1


class BinaryOperator(EvaluatableOperator):
    arity = 2


class Inc(UnaryOperator):
    name = "inc"

    def __call__(self, argument: OperatorArgument):
        if isinstance(argument, Number):
            return Number(argument.value + 1)
        else:
            raise NoEvalError()


class Dec(UnaryOperator):
    name = "dec"

    def __call__(self, argument: OperatorArgument):
        if isinstance(argument, Number):
            return Number(argument.value - 1)
        else:
            raise NoEvalError()


class Add(BinaryOperator):
    name = "add"

    def __call__(self, a1: OperatorArgument, a2: OperatorArgument):
        if isinstance(a1, Number) and isinstance(a2, Number):
            return Number(a1.value + a2.value)
        else:
            raise NoEvalError()


class Mul(BinaryOperator):
    name = "mul"

    def __call__(self, a1: OperatorArgument, a2: OperatorArgument):
        if isinstance(a1, Number) and isinstance(a2, Number):
            return Number(a1.value * a2.value)
        else:
            raise NoEvalError()


class Div(BinaryOperator):
    name = "div"

    def __call__(self, a1: OperatorArgument, a2: OperatorArgument):
        if isinstance(a1, Number) and isinstance(a2, Number):
            return Number(a1.value // a2.value)
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


class Eq(BinaryOperator):
    name = "eq"

    def __call__(self, a1: OperatorArgument, a2: OperatorArgument):
        if isinstance(a1, Number) and isinstance(a2, Number):
            return a1.value == a2.value

        # TODO HMM Do we want this?
        if a1 == a2:
            return True

        raise NoEvalError()


class Lt(BinaryOperator):
    name = "lt"

    def __call__(self, a1: OperatorArgument, a2: OperatorArgument):
        if isinstance(a1, Number) and isinstance(a2, Number):
            return Number(a1.value < a2.value)
        else:
            raise NoEvalError()


operators = {op().name: op() for op in (Inc, Dec, Add, Mul, Div, T, F, Lt)}

max_operator_arity = 2
