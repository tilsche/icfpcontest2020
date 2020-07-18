from abc import ABC, abstractmethod
from typing import Callable, Iterable, Iterator, List, Optional, Union

from .var_map import VarMap


class NoEvalError(RuntimeError):
    pass


class Node(ABC):
    children: List["Node"] = []

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

    def apply(self, f):
        f(self)
        for c in self.children:
            c.apply(f)

    @property
    def sugar(self):
        this = self
        try:
            this = self.as_list
        except:
            pass
            try:
                this = self.as_vector
            except:
                pass

        if not this.children:
            return this
        else:
            return type(this)(*(c.sugar for c in this.children))


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

    def __hash__(self):
        return hash((104, self.name))

    def copy(self, vm: Optional[VarMap] = None):
        return self

    def __str__(self):
        return f"{self.name}"


class SugarList(Node):
    def __init__(self, *children):
        self.children = children

    def __str__(self):
        inner = ", ".join((str(c) for c in self.children))
        return f"({inner})"

    def get(self):
        for c in self.children:
            yield c




class SugarVector(Node):
    def __init__(self, *children):
        self.children = children

    def __str__(self):
        assert len(self.children) == 2
        c1, c2 = self.children
        return f"<{c1}, {c2}>"




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
        return f"ap {self.children[0]} {self.children[1]}"

    def __repr__(self):
        return "Ap" + str((self.children[0], self.children[1]))

    @property
    def as_list(self):
        #         self    op          arg
        # must be (ap (ap cons head) tail)
        if (
            not isinstance(self.op, Ap)
            and isinstance(self.op.op, Operator)
            and self.op.op.name == "cons"
        ):
            raise TypeError(f"Not in list format: {self}")

        head = self.op.arg
        tail = self.arg
        return SugarList(head, *tail.as_list.children)

    @property
    def as_vector(self):
        #         self    op          arg
        # must be (ap (ap cons first) second)
        if (
            not isinstance(self.op, Ap)
            and isinstance(self.op.op, Operator)
            and self.op.op.name == "cons"
        ):
            raise TypeError(f"Not in list format: {self}")

        first = self.op.arg
        second = self.arg
        return SugarVector(first, second)


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

    def __hash__(self):
        return hash((208, self.id))
