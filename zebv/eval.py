from functools import reduce

from .node import Ap, Node, NoEvalError, Variable
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


class Evaluator:
    patterns = []

    def __init__(self, extra_patterns=None):
        self.patterns = default_patterns
        if extra_patterns:
            self.patterns = self.patterns + extra_patterns

    def simplify_once(self, node: Node):
        if isinstance(node, Ap):
            try:
                yield node.eval()
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
