from abc import abstractmethod
from typing import Union

from .node import Ap, Integer, Node, NoEvalError, Operator, Placeholder, SugarList

# OperatorArgument = Union[Integer, Variable]
OperatorArgument = Node


class HardcodedOperator(Operator):
    def __init__(self):
        assert self._value

    @classmethod
    def operators(cls):
        for c in cls.__subclasses__():
            if hasattr(c, "_value"):
                yield c
            for cc in c.operators():
                yield cc


class EvaluatableOperator(HardcodedOperator):
    _arity: int

    @abstractmethod
    def __call__(self, *args):
        raise NoEvalError()

    @property
    def arity(self):
        return self._arity


class UnaryOperator(EvaluatableOperator):
    _arity = 1

    @abstractmethod
    def __call__(self, x0: OperatorArgument):
        raise NoEvalError()


class BinaryOperator(EvaluatableOperator):
    _arity = 2

    @abstractmethod
    def __call__(self, x0: OperatorArgument, x1: OperatorArgument):
        raise NoEvalError()


class TenaryOperator(EvaluatableOperator):
    _arity = 3

    @abstractmethod
    def __call__(
        self, x0: OperatorArgument, x1: OperatorArgument, x2: OperatorArgument
    ):
        raise NoEvalError()


class Inc(UnaryOperator):
    _value = "inc"

    def __call__(self, argument: OperatorArgument):
        if isinstance(argument, Integer):
            return Integer(argument.value + 1)
        else:
            raise NoEvalError()


class Dec(UnaryOperator):
    _value = "dec"

    def __call__(self, argument: OperatorArgument):
        if isinstance(argument, Integer):
            return Integer(argument.value - 1)
        else:
            raise NoEvalError()


class Add(BinaryOperator):
    _value = "add"

    def __call__(self, a1: OperatorArgument, a2: OperatorArgument):
        if isinstance(a1, Integer) and isinstance(a2, Integer):
            return Integer(a1.value + a2.value)
        else:
            raise NoEvalError()


class Mul(BinaryOperator):
    _value = "mul"

    def __call__(self, a1: OperatorArgument, a2: OperatorArgument):
        if isinstance(a1, Integer) and isinstance(a2, Integer):
            return Integer(a1.value * a2.value)
        else:
            raise NoEvalError()


class Div(BinaryOperator):
    _value = "div"

    def __call__(self, a1: OperatorArgument, a2: OperatorArgument):
        if isinstance(a1, Integer) and isinstance(a2, Integer):
            return Integer(int(a1.value / a2.value))
        else:
            raise NoEvalError()


class Bool(BinaryOperator):
    pass


class T(Bool):
    _value = "t"

    def __call__(self, x0: OperatorArgument, x1: OperatorArgument):
        return x0


class F(Bool):
    _value = "f"

    def __call__(self, x0: OperatorArgument, x1: OperatorArgument):
        return x1


class Eq(BinaryOperator):
    _value = "eq"

    def __call__(self, a1: OperatorArgument, a2: OperatorArgument):
        if isinstance(a1, Integer) and isinstance(a2, Integer):
            if a1.value == a2.value:
                return T()
            else:
                return F()

        # TODO HMM Do we want this?
        if a1 == a2:
            return T()

        raise NoEvalError()


class Lt(BinaryOperator):
    _value = "lt"

    def __call__(self, a1: OperatorArgument, a2: OperatorArgument):
        if isinstance(a1, Integer) and isinstance(a2, Integer):
            if a1.value < a2.value:
                return T()
            else:
                return F()
        else:
            raise NoEvalError()


class Neg(UnaryOperator):
    _value = "neg"

    def __call__(self, a1: OperatorArgument):
        if isinstance(a1, Integer):
            return Integer(-a1.value)
        else:
            raise NoEvalError()


# for good checking, but no execution
class Cons(TenaryOperator):
    _value = "cons"

    def __call__(
        self, x0: OperatorArgument, x1: OperatorArgument, x2: OperatorArgument
    ):
        return Ap(Ap(x2, x0), x1)


class Nil(UnaryOperator):
    _value = "nil"

    @property
    def as_list(self):
        return SugarList()

    def __call__(self, x0: OperatorArgument):
        return T()


class IsNil(UnaryOperator):
    _value = "isnil"

    @property
    def as_list(self):
        return SugarList()

    def __call__(self, x0: OperatorArgument):
        if isinstance(x0, Nil):
            return T()
        if isinstance(x0, Ap) and isinstance(x0.op, Ap) and isinstance(x0.op.op, Cons):
            return F()
        raise NoEvalError()


class I(UnaryOperator):
    _value = "i"

    def __call__(self, a1: OperatorArgument):
        return a1


class S(TenaryOperator):
    _value = "s"

    def __call__(
        self, x0: OperatorArgument, x1: OperatorArgument, x2: OperatorArgument
    ):
        return Ap(Ap(x0, x2), Ap(x1, x2))


class C(TenaryOperator):
    _value = "c"

    def __call__(
        self, x0: OperatorArgument, x1: OperatorArgument, x2: OperatorArgument
    ):
        return Ap(Ap(x0, x2), x1)


class B(TenaryOperator):
    _value = "b"

    def __call__(
        self, x0: OperatorArgument, x1: OperatorArgument, x2: OperatorArgument
    ):
        return Ap(x0, Ap(x1, x2))


operators = {op().name: op() for op in HardcodedOperator.operators()}

max_operator_arity = 3
