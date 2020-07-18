import random
import time
from functools import lru_cache, reduce
from typing import Optional

from .node import Ap, Integer, Name, Node, NoEvalError, Operator, Placeholder
from .operators import Bool, Cons, EvaluatableOperator, F, Nil, T, max_operator_arity
from .patterns import (
    default_direct_patterns,
    default_expand_patterns,
    default_shrink_patterns,
)
from .var_map import VarMap


@lru_cache(4096)
def match(node: Node, pattern: Node):
    if isinstance(pattern, Placeholder):
        return VarMap({pattern.value: node})

    if type(node) != type(pattern):
        return False

    assert len(node.children) == len(pattern.children)

    if not node.children:
        if node == pattern:
            return VarMap()
        else:
            return False

    matches = [match(nc, pc) for nc, pc in zip(node.children, pattern.children)]
    if not all(matches):
        return False

    return reduce(VarMap.merge, matches)


def try_apply_operator(node, args=None):
    if not isinstance(node, Ap):
        return NoEvalError()

    op, arg = node.children

    if args is None:
        args = (arg,)
    else:
        args = (arg, *args)

    if isinstance(op, EvaluatableOperator):
        # <= ?
        if op._arity == len(args):
            return op(*args)

    if isinstance(op, Ap):
        # We need to go deeper
        if len(args) >= max_operator_arity:
            # Nah, no more than binary operators
            raise NoEvalError()

        return try_apply_operator(op, args)

    raise NoEvalError()


def contains_only(node, allowed_nodes):
    allowed_node_types = []
    allowed_operator_names = []
    for n in allowed_nodes:
        if isinstance(n, type):
            allowed_node_types.append(n)
        elif isinstance(n, str):
            allowed_operator_names.append(n)
        else:
            raise ValueError(f"Unknown contain check {n} (type {type(n)})")
    allowed_node_types = tuple(allowed_node_types)

    def test(node):
        if isinstance(node, allowed_node_types):
            return
        elif isinstance(node, Operator):
            if node.name in allowed_operator_names:
                return

        raise StopIteration()

    try:
        node.apply(test)
        return True
    except StopIteration:
        return False


t = T()
f = F()
nil = Nil()
cons = Cons()


class Evaluator:
    def __init__(self, shrink_patterns=(), expand_patterns=(), direct_patterns={}):
        assert not shrink_patterns
        assert not expand_patterns
        self.direct_patterns = default_direct_patterns
        self.direct_patterns.update(direct_patterns)

    def eval(self, node: Node) -> Node:
        if node.evaluated is not None:
            return node.evaluated
        initial_node = node
        while True:
            result = self.try_eval(node)
            if result == node:
                initial_node.evaluated = result
                return result
            node = result

    def try_eval(self, node: Node) -> Node:
        if node.evaluated is not None:
            return node.evaluated
        if isinstance(node, (Name, Operator)):
            try:
                return self.direct_patterns[node]
            except KeyError:
                pass
        if isinstance(node, Ap):
            fun = self.eval(node.op)
            x = node.arg
            if isinstance(fun, Operator):
                if fun.name == "neg":
                    xn = self.eval(x)
                    assert isinstance(xn, Integer)
                    return Integer(-xn.value)
                elif fun.name == "i":
                    return x
                elif fun.name == "nil":
                    return t
                elif fun.name == "isnil":
                    return Ap(x, Ap(t, Ap(t, f)))
                elif fun.name == "car":
                    return Ap(x, t)
                elif fun.name == "cdr":
                    return Ap(x, f)
            elif isinstance(fun, Ap):
                fun2 = self.eval(fun.op)
                y = fun.arg
                if isinstance(fun2, Operator):
                    if fun2.name == "t":
                        return y
                    if fun2.name == "f":
                        return x
                    if fun2.name in ("add", "mul", "div", "lt"):
                        xn = self.eval(x)
                        assert isinstance(xn, Integer)
                        yn = self.eval(y)
                        assert isinstance(yn, Integer)
                        if fun2.name == "add":
                            return Integer(xn.value + yn.value)
                        if fun2.name == "mul":
                            return Integer(xn.value * yn.value)
                        if fun2.name == "div":
                            return Integer(int(yn.value / xn.value))
                        if fun2.name == "lt":
                            return t if yn.value < xn.value else f
                        raise RuntimeError(fun2.name)
                    if fun2.name == "eq":
                        return t if self.eval(x) == self.eval(y) else f
                    if fun2.name == "cons":
                        return self.eval_cons(y, x)
                if isinstance(fun2, Ap):
                    fun3 = self.eval(fun2.op)
                    z = fun2.arg
                    if isinstance(fun3, Operator):
                        if fun3.name == "s":
                            return Ap(Ap(z, x), Ap(y, x))
                        elif fun3.name == "c":
                            return Ap(Ap(z, x), y)
                        elif fun3.name == "b":
                            return Ap(z, Ap(y, x))
                        elif fun3.name == "cons":
                            return Ap(Ap(x, z), y)
        return node

    def eval_cons(self, a: Node, b: Node):
        res = Ap(Ap(cons, self.eval(a)), self.eval(b))
        res.evaluated = res
        return res

    def simplify(
        self, expression: Node, stop_types=(Integer, Placeholder, Bool)
    ) -> Node:
        return self.eval(expression)
        # return sorted(visited_exprs, key=len)[0]

    def shrink(self, expression: Node):
        return self.eval(expression)
