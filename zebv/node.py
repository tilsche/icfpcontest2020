from abc import ABC, abstractmethod
from typing import Callable, Iterable, Iterator, List, Optional, Union

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
        return type(self)(*(c.copy(vm) for c in self.children))

    # def __str__(self):
    #     cstr = ", ".join((str(c) for c in self.children))
    #     return f"[{type(self).__name__}: {cstr}]"

    def __str__(self):
        cstr = " ".join((str(c) for c in self.children))
        return f"{type(self).__name__.lower()} {cstr}"

    def __repr__(self):
        return str(self)


class Number(Node):
    value: int

    def __init__(self, value: int):
        assert type(value) == int
        self.value = value

    def __eq__(self, other):
        return isinstance(other, Number) and self.value == other.value

    def copy(self, vm: Optional[VarMap] = None):
        return Number(self.value)

    def __str__(self):
        return str(self.value)


class Variable(Node):
    id: int

    def __init__(self, id: int):
        self.id = id

    def __eq__(self, other):
        return isinstance(other, Variable) and self.id == other.id

    def copy(self, vm: Optional[VarMap] = None):
        if vm:
            return vm[self.id].copy()
        return Variable(self.id)

    def __str__(self):
        return f"x{self.id}"


class Equals(Node):
    def __init__(self, left: Node, right: Node):
        self.children = [left, right]


class Operator(Node):
    name: str

    def __eq__(self, other):
        return isinstance(other, Operator) and self.name == other.name

    def copy(self, vm: Optional[VarMap] = None):
        return self

    def __str__(self):
        return f"{self.name}"


class Ap(Node):
    def __init__(self, op: Union[Operator, Callable, "Variable", "Name"], arg: Node):
        self.children = [op, arg]

    def eval(self):
        op, arg = self.children
        if isinstance(op, (Callable, Operator)):
            return op(arg)
        raise NoEvalError()

    @property
    def op(self):
        return self.children[0]

    @property
    def arg(self):
        return self.children[1]

    def __str__(self):
        return "ap {self.children[0]} {self.children[1]}".format(self=self)

    def __repr__(self):
        return "Ap" + str((self.children[0], self.children[1]))


class GenericOperator(Operator):
    def __init__(self, name: str):
        self.name = name


class Name(Node):
    id: int

    def __init__(self, id: int):
        self.id = id

    def __eq__(self, other):
        return type(other) == Name and self.id == other.id

    def copy(self, vm: Optional[VarMap] = None):
        return self

    def __call__(self, *args, **kwargs):
        raise NoEvalError()

    def __str__(self):
        return f":{self.id}"
