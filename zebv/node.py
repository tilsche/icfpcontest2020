from abc import ABC, abstractmethod
from functools import cached_property, reduce
from typing import Callable, Dict, Iterable, Iterator, List, Optional, Set, Tuple, Union

from .var_map import VarMap


class NoEvalError(RuntimeError):
    pass


class Node(ABC):
    _children: List["Node"]
    _dirty: bool = True
    # This is so gonna leak lol
    _parents: Dict[Tuple[int, int], "Node"]

    def __init__(self, *children):
        self._parents = {}
        for index, c in enumerate(children):
            c.add_parent(self, index)
        self._children = list(children)

    @property
    def children(self) -> Tuple["Node"]:
        return self._children

    def swap_child(self, index: int, new_child: "Node"):
        self._children[index].remove_parent(self, index)
        new_child.add_parent(self, index)
        self._children[index] = new_child
        self.dirty = True

    def add_parent(self, parent, index):
        assert id(self) != id(parent)
        key = id(parent), index
        assert key not in self._parents
        self._parents[key] = parent

    def remove_parent(self, parent, index):
        key = id(parent), index
        assert key in self._parents
        del self._parents[key]

    def __eq__(self, other):
        return type(self) == type(other) and self.children == other.children

    @property
    def check_dirty_consistency(self):
        clean_children = True
        for c in self.children:
            clean_children = clean_children and not c.dirty
        if not self._dirty:
            assert clean_children

    @property
    def dirty(self):
        # self.check_dirty_consistency
        return self._dirty

    @dirty.setter
    def dirty(self, value):
        was_dirty = self._dirty
        self._dirty = value
        if not was_dirty and value:
            for parent in self._parents.values():
                parent.dirty = True

    # @cached_property
    @property
    def __hash(self):
        return hash((type(self), tuple(self.children)))

    # @cached_property
    @property
    def __len(self):
        return 1 + sum((c.__len for c in self.children))

    def __hash__(self):
        return self.__hash

    def __len__(self):
        return self.__len

    # @cached_property
    def __placeholders(self):
        return set.union(*(c.__placeholders for c in self.children))

    def instantiate(self, vm: VarMap) -> "Node":
        if not vm:
            return self
        # if not self.__placeholders:
        #     return self
        # assert self.__placeholders.issubset(vm)

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
        self._parents = {}
        self._value = value

    def __hash__(self):
        return hash((type(self), self._value))

    def instantiate(self, vm: VarMap):
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

    def __placeholders(self):
        return set()


class Integer(LeafNode):
    pass


class Placeholder(LeafNode):
    def instantiate(self, vm: VarMap):
        return vm[self._value]

    def __str__(self):
        return f"x{self._value}"

    def __repr__(self):
        return f"Variable(x{self._value})"

    def __placeholders(self):
        return set((self._value,))


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


class HardcodedOperator(Operator):
    def __init__(self):
        self._parents = {}
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
    max_arity = 3

    @abstractmethod
    def __call__(self, *args):
        raise NoEvalError()

    @property
    def arity(self):
        return self._arity


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
        # # Try to evaluate right now!
        # eval_op = op
        # assert EvaluatableOperator.max_arity == 3
        # # some premature optimization
        # if isinstance(op, EvaluatableOperator) and op.arity == 1:
        #     try:
        #         arg =
        #
        # remaining_arity = None
        # if isinstance(op, EvaluatableOperator):
        #     remaining_arity = op.arity - 1
        # elif isinstance(op, Ap) and op._remaining_arity is not None:
        #     remaining_arity = op._remaining_arity
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
