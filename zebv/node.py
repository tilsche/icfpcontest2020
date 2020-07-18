from abc import ABC, abstractmethod
from functools import cached_property
from typing import Callable, Iterable, Iterator, List, Optional, Tuple, Union

from .var_map import VarMap


class NoEvalError(RuntimeError):
    pass


class Node(ABC):
    _children: Tuple["Node"]

    def __init__(self, *children):
        self._children = children

    @property
    def children(self) -> Tuple["Node"]:
        return self._children

    def __eq__(self, other):
        return type(self) == type(other) and self.children == other.children

    def __hash__(self):
        return hash((type(self), self.children))

    def __len__(self):
        return self.__len

    @cached_property
    def __len(self):
        return 1 + sum((c.__len for c in self.children))

    def instantiate(self, vm: Optional[VarMap] = None):
        return type(self)(*(c.instantiate(vm) for c in self.children))

    def __str__(self):
        cstr = " ".join((str(c) for c in self.children))
        return f"{type(self).__name__.lower()} {cstr}"

    def __repr__(self):
        return f"Node(children={self.children!r})"

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


class LeafNode(Node):
    _children = ()
    _value: Union[int, str]

    def __init__(self, value: Union[int, str]):
        self._value = value

    def __hash__(self):
        return hash((type(self), self._value))

    def instantiate(self, vm: Optional[VarMap] = None):
        return self

    @property
    def value(self):
        return self._value

    def __eq__(self, other):
        return type(self) == type(other) and self._value == other.value

    def __str__(self):
        return str(self.value)

    def __repr__(self):
        return f"{type(self)}({self.value!r})"


class Integer(LeafNode):
    pass


class Placeholder(LeafNode):
    def instantiate(self, vm: Optional[VarMap] = None):
        if vm:
            return vm[self._value]
        return self

    def __str__(self):
        return f"x{self._value}"

    def __repr__(self):
        return f"Variable(x{self._value})"


class Equals(Node):
    def __init__(self, left: Node, right: Node):
        super.__init__(left, right)


class Operator(LeafNode):
    def __eq__(self, other):
        return isinstance(other, Operator) and self._value == other._value

    def __hash__(self):
        return hash((42, self._value))

    @property
    def name(self):
        return self._value


class SugarList(Node):
    def __str__(self):
        inner = ", ".join((str(c) for c in self.children))
        return f"({inner})"

    def __repr__(self):
        inner_reps = ", ".join(repr(i) for i in self.children)
        return f"SugarList({inner_reps})"

    def __iter__(self):
        return iter(self.children)


class SugarVector(Node):
    def __init__(self, left: Node, right: Node):
        super().__init__(left, right)

    def __str__(self):
        c1, c2 = self.children
        return f"<{c1}, {c2}>"

    def __repr__(self):
        c1, c2 = self.children
        return f"SugarVector<{c1!r}, {c2!r}>"


class Ap(Node):
    def __init__(self, op: Union[Operator, "Placeholder", "Name"], arg: Node):
        super().__init__(op, arg)

    @property
    def op(self):
        return self.children[0]

    @property
    def arg(self):
        return self.children[1]

    def __str__(self):
        return f"ap {self.op} {self.arg}"

    def __repr__(self):
        return f"Ap(op={self.op!r}, arg={self.arg!r})"

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
    pass


class Name(LeafNode):
    pass
