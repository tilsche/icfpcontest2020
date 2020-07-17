from copy import deepcopy
from functools import reduce

from .node import Ap, Node, NoEvalError, Variable
from .var_map import VarMap


def match(left: Node, right: Node):
    if isinstance(left, Variable):
        # if isinstance(right, Variable):
        #     if left.id == right.id:
        #         return VarMap()
        #     else:
        #         # Oh shit
        #         raise RuntimeError("I don't know what to do here.")
        return VarMap({left.id: right})

    if type(left) != type(right):
        return False

    assert len(left.children) == len(right.children)

    if not left.children:
        if left == right:
            return VarMap()
        else:
            return False

    matches = [match(lc, rc) for lc, rc in zip(left.children, right.children)]
    if not all(matches):
        return False

    return reduce(VarMap.merge, matches)


class Evaluator:
    patterns = []

    def __init__(self, patterns):
        self.patterns = patterns

    def simplify(self, node: Node):
        if isinstance(node, Ap):
            try:
                yield node.eval()
            except NoEvalError:
                pass

        for pattern, replacement in self.patterns:
            vm = match(node, pattern)
            if not vm:
                continue
            yield replacement.copy(vm)

        for index, child in enumerate(node.children):
            for simple_child in self.simplify(child):
                copy = node.copy()
                copy.children[index] = simple_child
                yield copy
