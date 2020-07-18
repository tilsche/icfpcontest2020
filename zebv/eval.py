import random
import time
from functools import lru_cache, reduce
from typing import Optional

from .node import Ap, Integer, Name, Node, NoEvalError, Operator, Placeholder
from .operators import Bool, EvaluatableOperator, max_operator_arity
from .patterns import (
    default_direct_patterns,
    default_expand_patterns,
    default_shrink_patterns,
)
from .var_map import VarMap


# @lru_cache(4096)
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


class Evaluator:
    def __init__(self, shrink_patterns=(), expand_patterns=(), direct_patterns={}):
        self.shrink_patterns = default_shrink_patterns + list(shrink_patterns)
        self.expand_patterns = default_expand_patterns + list(expand_patterns)
        self.direct_patterns = default_direct_patterns
        self.direct_patterns.update(direct_patterns)

    # @lru_cache(4096)
    def shrink_once(self, node: Node) -> Optional[Node]:
        if isinstance(node, Ap):
            try:
                return try_apply_operator(node)
            except NoEvalError:
                pass

        for pattern, replacement in self.shrink_patterns:
            vm = match(node, pattern)
            if not vm:
                continue
            return replacement.instantiate(vm)

        if not node.children:
            # Nothing to simplify here
            return None

        for idx, child in enumerate(node.children):
            shrinked_child = self.shrink_once(child)
            if shrinked_child is not None:
                node._children[idx] = shrinked_child
                return node

        return None

    def shrink(self, node: Node) -> Node:
        while True:
            next_node = self.shrink_once(node)
            if next_node is None:
                return node
            node = next_node
            # print(f"[Shrink] {node}")

    # def expand_once(self, node: Node):
    #     if not node.children:
    #         if isinstance(node, (Operator, Name)):
    #             try:
    #                 yield self.direct_patterns[node]
    #             except KeyError:
    #                 pass
    #     else:
    #         for index, child in enumerate(node.children):
    #             for expanded_child in self.expand_once(child):
    #                 new_children = list(node.children)
    #                 new_children[index] = expanded_child
    #                 copy = type(node)(*new_children)
    #                 yield copy
    #
    #         for pattern, replacement in self.expand_patterns:
    #             vm = match(node, pattern)
    #             if not vm:
    #                 continue
    #             yield replacement.copy(vm)

    def expand_once_direct(self, node: Node):
        if not node.children:
            if isinstance(node, (Operator, Name)):
                try:
                    return self.direct_patterns[node]
                except KeyError:
                    return None
        else:
            for index, child in enumerate(node.children):
                expanded_child = self.expand_once_direct(child)
                if expanded_child:
                    node._children[index] = expanded_child
                    return node
        return None

    def expand_once_pattern(self, node: Node):
        raise NotImplementedError()
        # if not node.children:
        #     return
        # for index, child in enumerate(node.children):
        #     for expanded_child in self.expand_once_pattern(child):
        #         new_children = list(node.children)
        #         new_children[index] = expanded_child
        #         copy = type(node)(*new_children)
        #         yield copy

        for pattern, replacement in self.expand_patterns:
            raise RuntimeError("not implemented for new instatiate")
            # vm = match(node, pattern)
            # if not vm:
            #     continue
            # yield replacement.instantiate(vm)

    def expand_once(self, node: Node):
        return self.expand_once_direct(node)
        if self.expand_patterns:
            return self.expand_once_pattern(node)

    def simplify(
        self, expression: Node, stop_types=(Integer, Placeholder, Bool)
    ) -> Node:
        start = time.time()
        for step in range(100000):
            expression = self.shrink(expression)

            if step % 100 == 0:
                rate = step / (time.time() - start)
                print(f"[{step} | {rate:.1f} 1/s] ({len(expression)}): {expression}")
            if contains_only(expression, stop_types):
                return expression

            expression = self.expand_once(expression)
            assert expression is not None

        print("giving up")
        raise RuntimeError("Timeout")
        # return sorted(visited_exprs, key=len)[0]
