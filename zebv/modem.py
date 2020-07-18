from logging import getLogger
from math import ceil
from typing import Tuple, Union

from .node import Ap, Number, Node
from .operators import Cons, Nil

logger = getLogger(__name__)


def mod_num(input: int) -> str:
    abs_val = int(abs(input))
    if abs_val == 0:
        return "010"
    else:
        pos_or_neg = "01" if input >= 0 else "10"
        bit_len = abs_val.bit_length()

        n = ceil(bit_len / 4)

        unary_len = "1" * n + "0"

        return f"{pos_or_neg}{unary_len}{abs_val:0{4*n}b}"


def mod(input) -> str:
    if isinstance(input, int):
        return mod_num(input)
    elif isinstance(input, tuple):
        arity = len(input)
        if arity == 0:
            return "00"
        elif arity == 2:
            head = mod(input[0])
            tail = mod(input[1])
            return f"11{head}{tail}"
        else:
            raise ValueError(f"Expected tuple of length 0 or 2, got {arity}")
    else:
        raise TypeError(f"The fuck is this? input={input}")


def _to_tuple_list(node: Union[Ap, Number, Nil]):
    if isinstance(node, Number):
        return int(node.value)
    elif isinstance(node, Nil):
        return ()
    elif isinstance(node, Ap):
        first_ap = node.op
        arg = node.arg
        if isinstance(first_ap, Ap) and isinstance(first_ap.op, Cons):
            return (_to_tuple_list(first_ap.arg), _to_tuple_list(arg))
        else:
            raise ValueError(f'Node {node!r} is not in the form of "ap ap cons _"')
    else:
        raise ValueError(f'Node {node!r} is neither a number, "nil" nor an "ap cons"')


def _from_tuple_list(tuple_list) -> Node:
    if isinstance(tuple_list, int):
        return Number(tuple_list)
    elif isinstance(tuple_list, tuple):
        arity = len(tuple_list)
        if arity == 0:
            return Nil()
        elif arity == 2:
            (left, right) = tuple_list
            return Ap(Ap(Cons(), _from_tuple_list(left)), _from_tuple_list(right))
        else:
            raise ValueError(f"Invalid tuple_list {tuple_list!r}")
    else:
        raise ValueError(f"Invalid tuple_list {tuple_list!r}")


def mod_node(node: Union[Ap, Number, Nil]) -> str:
    return mod(_to_tuple_list(node))


def demod_num(input: str) -> (int, str):
    bits = 0
    while True:
        (fst, input) = input[0], input[1:]
        if fst == "1":
            bits += 1
        else:
            break

    if not bits:
        return (0, input)
    else:
        value_len = bits * 4
        (value, rest) = input[:value_len], input[value_len:]
        return (int(value, base=2), rest)


def demod(input: str) -> Union[Tuple, int]:
    def demod_impl(input: str) -> (Union[Tuple, int], str):
        (type_, value) = (input[:2], input[2:])

        if type_ == "00":
            return ((), value)
        elif type_ == "01":
            (num, rest) = demod_num(value)
            return (1 * num, rest)
        elif type_ == "10":
            (num, rest) = demod_num(value)
            return (-1 * num, rest)
        elif type_ == "11":
            (head, tail) = demod_impl(value)
            (tail, rest) = demod_impl(tail)
            return ((head, tail), rest)
        else:
            raise ValueError(f"Unexpected type {type_!r}")

    (result, rest) = demod_impl(input)
    return result


def demod_node(input: str) -> Node:
    return _from_tuple_list(demod(input))
