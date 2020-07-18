from .eval import Evaluator, match
from .node import Ap, Number
from .operators import Cons, Nil
from .parsing import build_expression
from .patterns import parse_patterns


class Interaction:
    def __init__(self, text, protocol):
        patterns = parse_patterns(text)
        self.evaluator = Evaluator(*patterns)
        self.protocol = build_expression(protocol)
        self.state = Nil()

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
        print(f"should draw: {data}")

    def send(self, data):
        print(f"should send {data}")
        raise RuntimeError("send not implemented")
        pass

    def step(self, vector):
        # expr = Ap(Ap(Ap(self.interact, self.protocol), self.state), vector)
        # nexpr = self.evaluator.simplify(
        #     expr, (Ap, Cons, Nil, Number, "f38", self.protocol.name)
        # )
        # f38_map = match(nexpr, self.f38_pattern)
        # assert f38_map
        # print(f38_map.map)
        proto_expr = Ap(Ap(self.protocol, self.state), vector)
        proto_result = self.evaluator.simplify_linear(
            proto_expr, (Ap, Cons, Nil, Number)
        )
        # This will probably crash, sorry
        flag, new_state, data = proto_result.as_list.children

        print(f"flag: {flag}")
        print(f"new_state: {new_state.sugar}")
        print(f"data: {data.sugar}")

        self.state = new_state
        if flag.value == 0:
            self.draw(data)
        else:
            self.step(self.send(data))

    def __call__(self, x: int, y: int):
        self.step(build_expression(f"ap ap vec {x} {y}"))
