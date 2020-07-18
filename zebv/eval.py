from functools import reduce

from .node import Ap, Node, NoEvalError, Number, Operator, Variable
from .operators import Bool, EvaluatableOperator, max_operator_arity
from .patterns import default_patterns
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
    patterns = []

    def __init__(self, extra_patterns=None):
        self.patterns = default_patterns
        if extra_patterns:
            self.patterns = self.patterns + extra_patterns

    def simplify_once(self, node: Node):
        if isinstance(node, Ap):
            try:
                yield try_apply_operator(node)
                return
            except NoEvalError:
                pass

        for pattern, replacement in self.patterns:
            vm = match(node, pattern)
            if not vm:
                continue
            yield replacement.copy(vm)

        for index, child in enumerate(node.children):
            for simple_child in self.simplify_once(child):
                copy = node.copy()
                copy.children[index] = simple_child
                yield copy

    def simplify(self, expression: Node, stop_types=(Number, Variable, Bool)):
        todo_exprs = [expression]
        todo_strs = set((str(expression),))

        visited_exprs = []
        visited_strs = set()

        for _ in range(10000):
            if not todo_exprs:
                return sorted(visited_exprs, key=len)[0]

            todo_exprs = list(sorted(todo_exprs, key=len))
            current = todo_exprs[0]
            todo_exprs = todo_exprs[1:]
            todo_strs.remove(str(current))
            print(f"looking at: {current}")

            for candidate in self.simplify_once(current):
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
        return sorted(visited_exprs, key=len)[0]
