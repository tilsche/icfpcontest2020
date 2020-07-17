from abc import ABC, abstractmethod
from typing import Callable, Iterable, Iterator, List, Optional, Union

from . import parsing
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

    def __str__(self):
        cstr = ", ".join((str(c) for c in self.children))
        return f"[{type(self).__name__}: {cstr}]"

    def __repr__(self):
        return str(self)


class Number(Node):
    value: int

    def __init__(self, value: int):
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
        return Variable(id)

    def __str__(self):
        return f"x{self.id}"


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
    def __init__(self, op: Union[Operator, Callable, "Variable", "Name"], arg: Node):
        self.children = [op, arg]

    def eval(self):
        op, arg = self.children
        if isinstance(op, (Callable, Operator)):
            return op(arg)
        raise NoEvalError()


class Inc(Operator):
    def __call__(self, argument: Union[Number, Variable]):
        if type(argument) == Number:
            return Number(argument.value + 1)
        else:
            raise NoEvalError()

    def __str__(self):
        return "inc"


class GenericOperator(Operator):
    id: str

    def __init__(self, id: str):
        self.id = id

    def __eq__(self, other):
        return type(other) == GenericOperator and self.id == other.id

    def copy(self, vm: Optional[VarMap] = None):
        return self

    def __call__(self, *args, **kwargs):
        raise NoEvalError()

    def __str__(self):
        return f":{self.id}"


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


def _parse_expression(tokens: Iterator[parsing.Token]):
    tok = next(tokens)

    if isinstance(tok, parsing.Literal):
        if tok.name == "ap":
            return Ap(_parse_expression(tokens), _parse_expression(tokens))

        if tok.name in ["?", "=", "=="]:
            raise ValueError(f"strange token {tok}")

        if tok.name.startswith("x"):
            return Variable(int(tok.name[1:]))

        # Assume operator
        return GenericOperator(tok.name)

    if isinstance(tok, parsing.ColonName):
        return Name(tok._id)

    if isinstance(tok, parsing.IntLiteral):
        return Number(tok.value)

    raise TypeError(f"unknown token type: {type(tok)} {tok}")


def build_expression(tokens: Iterable[parsing.Token]):
    it = iter(tokens)
    expression = _parse_expression(it)
    rest = list(it)
    if rest:
        raise RuntimeError(f"Tokens not all consumed: {rest}")
    return expression
