import os
import time
from logging import getLogger
from typing import Callable

from .api import ApiClient
from .eval import Evaluator
from .expression import Ap, Expression, as_list, as_vector, build_expression
from .modem import demod_node, mod_node
from .screen import AlienScreen, Coord

logger = getLogger(__name__)


class Interaction:
    def __init__(
        self,
        text,
        protocol,
        send_function: Callable[[Expression], Expression] = None,
        interactive=False,
    ):
        self.evaluator = Evaluator(text)
        self.protocol = build_expression(protocol)
        self.state = "nil"
        self.api_client = ApiClient(
            "https://icfpc2020-api.testkontur.ru/", os.environ["PLAYER_KEY"]
        )
        self.send_function = self.api_client.aliens_send
        self.screen = None
        if interactive:
            self.screen = AlienScreen()
            self.screen.start()
            self.iteration = 0
            self.protocol_name = protocol

            def callback(point):
                self(point.x, point.y)

            self.screen.on_mouse_click = callback

    def draw(self, data):
        logger.debug(f"should draw: {data}")
        if self.screen:
            for l in as_list(data):
                self.screen.draw(as_list(l))

    def send(self, data: Expression) -> Expression:
        logger.warning(f"Should send {data}...")
        if self.send_function:
            res = self.send_function(mod_node(data))
            return demod_node(res)
        else:
            raise RuntimeError("No send_function function supplied")

    def step(self, vector):
        proto_expr = Ap(Ap(self.protocol, self.state), vector)
        start_simplify = time.time()
        proto_result = self.evaluator.eval(proto_expr)
        duration = time.time() - start_simplify
        logger.warning(f"Step took {duration} s")

        # This will probably crash, sorry
        flag, new_state, data = as_list(proto_result)

        logger.debug(
            f"[{duration} s] {__name__}: flag={flag!r}, new_state={new_state!r}, data={data}"
        )

        self.state = new_state
        if flag == 0:
            self.draw(data)
        else:
            self.step(self.send(data))

    def __call__(self, x: int, y: int):
        logger.warning(f"Click {x} {y}")
        if self.screen:
            self.screen.save(f"{self.protocol_name}-{self.iteration}.png", Coord(x, y))
            self.iteration += 1
        self.screen.clear()
        self.step(build_expression(f"ap ap vec {x} {y}"))
