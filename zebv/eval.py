import random
import time
from functools import reduce
from typing import Optional

from .node import Ap, Name, Node, NoEvalError, Number, Operator, Variable
from .operators import Bool, EvaluatableOperator, max_operator_arity
from .patterns import (
    default_direct_patterns,
    default_expand_patterns,
    default_shrink_patterns,
)
from .var_map import VarMap


def match(node: Node, pattern: Node):
    if isinstance(pattern, Variable):
        # if isinstance(right, Variable):
        #     if left.id == right.id:
        #         return VarMap()
        #     else:
        #         # Oh shit
        #         raise RuntimeError("I don't know what to do here.")
        return VarMap({pattern.id: node})

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
        if op.arity == len(args):
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

    def shrink_once(self, node: Node) -> Optional[Node]:
        if isinstance(node, Ap):
            try:
                return try_apply_operator(node)
            except NoEvalError:
                pass

        shrinked = None
        for pattern, replacement in self.shrink_patterns:
            vm = match(node, pattern)
            if not vm:
                continue
            assert shrinked is None
            # keep going just to see that no two patterns ever match. Then we must try more ways...
            shrinked = replacement.copy(vm)

        if shrinked is not None:
            return shrinked

        if not node.children:
            # Nothing more to simplify
            return None

        shrinked_children = False
        children = []
        for child in node.children:
            simple_child = self.shrink_once(child)
            if simple_child is not None:
                children.append(simple_child)
                shrinked_children = True
            else:
                children.append(child)

        if shrinked_children:
            return type(node)(*children)

        return None

    def shrink(self, node: Node) -> Node:
        while True:
            next_node = self.shrink_once(node)
            if next_node is None:
                return node
            node = next_node
            # print(f"[Shrink] {node}")

    def expand_once(self, node: Node):
        if not node.children:
            if isinstance(node, (Operator, Name)):
                try:
                    yield self.direct_patterns[node]
                except KeyError:
                    pass
        else:
            for pattern, replacement in self.expand_patterns:
                vm = match(node, pattern)
                if not vm:
                    continue
                yield replacement.copy(vm)

        for index, child in enumerate(node.children):
            for expanded_child in self.expand_once(child):
                new_children = list(node.children)
                new_children[index] = expanded_child
                copy = type(node)(*new_children)
                yield copy

    def simplify(self, expression: Node, stop_types=(Number, Variable, Bool)) -> Node:
        start = time.time()

        expression = self.shrink(expression)
        if contains_only(expression, stop_types):
            return expression

        todo_exprs = [expression]
        todo_strs = set((str(expression),))

        visited_exprs = []
        visited_strs = set()

        for i in range(10000):
            if not todo_exprs:
                raise RuntimeError("not found")
                # return sorted(visited_exprs, key=len)[0]

            todo_exprs = list(sorted(todo_exprs, key=len))
            current = todo_exprs[0]
            todo_exprs = todo_exprs[1:]
            todo_strs.remove(str(current))

            if i % 10 == 0:
                rate = i / (time.time() - start)
                print(
                    f"BFS [{i} | {1+len(todo_exprs)} | {rate:.1f} 1/s] ({len(current)}): {current}"
                )

            for candidate in self.expand_once(current):
                # print(f"Candidate: {candidate}")
                candidate = self.shrink(candidate)
                s = str(candidate)
                if s in visited_strs or s in todo_strs:
                    continue

                if contains_only(candidate, stop_types):
                    return candidate

                visited_strs.add(s)
                todo_strs.add(s)

                todo_exprs.append(candidate)
                visited_exprs.append(candidate)

        print("giving up")
        raise RuntimeError("Timeout")
        # return sorted(visited_exprs, key=len)[0]

    def simplify_linear(
        self, expression: Node, stop_types=(Number, Variable, Bool)
    ) -> Node:
        start = time.time()
        for step in range(10000):
            expression = self.shrink(expression)

            if step % 10 == 0:
                rate = step / (time.time() - start)
                print(f"[{step} | {rate:.1f} 1/s] ({len(expression)}): {expression}")
            if contains_only(expression, stop_types):
                return expression

            expression = random.choice(list(self.expand_once(expression)))

        print("giving up")
        raise RuntimeError("Timeout")
        # return sorted(visited_exprs, key=len)[0]
