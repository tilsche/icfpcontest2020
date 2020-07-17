from abc import ABC, abstractmethod
from typing import Callable, List, Optional, Union

from .var_map import VarMap


class NoEvalError(RuntimeError):
    pass


class Node(ABC):
    children: List["Node"] = []

    def match(self, pattern: "Node"):
        if not self.children:
            if self == pattern:
                return {}
            else:
                return False

        return

    def __eq__(self, other):
        return type(self) == type(other) and self.children == other.children

    def __len__(self):
        return 1 + sum((len(c) for c in self.children))

    def copy(self, vm: Optional[VarMap] = None):
        return type(self)(*self.children)


class Number(Node):
    value: int

    def __init__(self, value: int):
        self.value = value

    def __eq__(self, other):
        return isinstance(other, Number) and self.value == other.value

    def copy(self, vm: Optional[VarMap] = None):
        return Number(self.value)


class Variable(Node):
    id: int

    def __init__(self, id: int):
        self.id = id

    def __eq__(self, other):
        return isinstance(other, Variable) and self.id == other.id

    def copy(self, vm: Optional[VarMap] = None):
        if vm:
            return vm[self.id].copy()
        return Variable(id)


class Equals(Node):
    def __init__(self, left: Node, right: Node):
        self.children = [left, right]


class Operator(Node):
    @abstractmethod
    def __call__(self, argument):
        raise NoEvalError()


# class Ap(Node):
#     op: Union[Operator, Callable]
#     arguments: List[Node]
#
#     def __init__(self, op: Union[Operator, Callable], args: List[Node]):
#         self.op = op
#         self.args = args
#
#     def __call__(self):
#         op = self.op(self.args[0])
#         args = self.args[1:]
#         if args:
#             return Ap(op, args)
#         else:
#             return op


class Ap(Node):
    def __init__(self, op: Union[Operator, Callable, Node], arg: Node):
        self.children = [op, arg]

    def eval(self):
        op, arg = self.children()
        if isinstance(op, (Callable, Operator)):
            return op(arg)


class Inc(Operator):
    def __call__(self, argument: Union[Number, Variable]):
        if type(argument) == Number:
            return Number(argument.value + 1)
        else:
            raise NoEvalError()


class GenericOperator(Operator):
    id: int

    def __init__(self, id: int):
        self.id = id

    def __eq__(self, other):
        return type(other) == GenericOperator and self.id == other.id

    def copy(self, vm: Optional[VarMap] = None):
        return self

    def __call__(self, *args, **kwargs):
        raise NoEvalError()
