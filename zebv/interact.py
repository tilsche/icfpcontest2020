from logging import getLogger
from typing import Callable

from .eval import Evaluator
from .node import Ap, Integer, Node
from .operators import Cons, Nil
from .parsing import build_expression
from .patterns import parse_patterns
from .screen import AlienScreen

logger = getLogger(__name__)


class Interaction:
    def __init__(self, text, protocol, send_function: Callable[[Node], Node] = Node):
        patterns = parse_patterns(text)
        self.evaluator = Evaluator(*patterns)
        self.protocol = build_expression(protocol)
        self.state = Nil()
        self.send_function = send_function
        self.screen = AlienScreen()
        self.screen.start()

        # self.draw_pattern = build_expression(
        #     #         newState                      draw_list
        #     "ap ap cons x1 ap ap cons ap multipledraw x2 nil"
        # )
        # self.send_pattern = build_expression(
        #     #                             newState   data
        #     f"ap ap ap interact {protocol} x1 ap send x2"
        # )
        # self.f38_pattern = build_expression(
        #     #                                flag         newState        data
        #     f"ap ap f38 {protocol} ap ap cons x2 ap ap cons x3 ap ap const x4 nil"
        # )

    def draw(self, data):
        logger.warning(f"should draw: {data}")
        for list in data.as_list:
            self.screen.draw(list.as_list)

    def send(self, data: Node) -> Node:
        logger.warning(f"Should send {data}...")
        if self.send_function:
            self.send_function(data)
        else:
            raise RuntimeError("No send_function function supplied")

    def step(self, vector):
        # expr = Ap(Ap(Ap(self.interact, self.protocol), self.state), vector)
        # nexpr = self.evaluator.simplify(
        #     expr, (Ap, Cons, Nil, Number, "f38", self.protocol.name)
        # )
        # f38_map = match(nexpr, self.f38_pattern)
        # assert f38_map
        # print(f38_map.map)
        proto_expr = Ap(Ap(self.protocol, self.state), vector)
        proto_result = self.evaluator.simplify(proto_expr, (Ap, Cons, Nil, Integer))
        # This will probably crash, sorry
        flag, new_state, data = proto_result.as_list.children

        logger.debug(
            f"{__name__}: flag={flag!r}, new_state={new_state!r}, data={data.sugar}"
        )

        self.state = new_state
        if flag.value == 0:
            self.draw(data)
        else:
            self.step(self.send(data))

    def __call__(self, x: int, y: int):
        self.step(build_expression(f"ap ap vec {x} {y}"))
