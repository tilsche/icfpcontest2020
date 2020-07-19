import time
from logging import getLogger
from typing import Callable

from .eval import Evaluator
from .expression import Ap, Expression, as_list, as_vector, build_expression
from .screen import AlienScreen

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
        self.send_function = send_function
        self.screen = None
        if interactive:
            self.screen = AlienScreen()
            self.screen.start()
            self.iteration = 0
            self.protocol_name = protocol

            def callback(x, y):
                self.screen.clear()
                self(x, y)

            self.screen.on_mouse_click = callback

    def draw(self, data):
        logger.warning(f"should draw: {data}")
        if self.screen:
            for l in as_list(data):
                self.screen.draw(as_list(l))
            self.screen.save(f"{self.protocol_name}-{self.iteration}.png")
            self.iteration += 1

    def send(self, data: Expression) -> Expression:
        logger.warning(f"Should send {data}...")
        if self.send_function:
            self.send_function(data)
        else:
            raise RuntimeError("No send_function function supplied")

    def step(self, vector):
        proto_expr = Ap(Ap(self.protocol, self.state), vector)
        start_simplify = time.time()
        proto_result = self.evaluator.eval(proto_expr)
        duration = time.time() - start_simplify

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
        self.step(build_expression(f"ap ap vec {x} {y}"))
