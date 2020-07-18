from zebv.eval import Evaluator
from zebv.node import Ap, Integer
from zebv.operators import Cons, Nil
from zebv.parsing import build_expression, tokenize
from zebv.screen import AlienScreen


def t(exp):
    return build_expression(tokenize(exp))


def t_list(vecs):
    res = []
    for v in vecs.split(","):
        res.append(t(v))
    return res


def test_screen():
    screen = AlienScreen()
    screen.start()

    e = Evaluator()
    data_list_1 = e.simplify(
        build_expression(tokenize("ap ap checkerboard 7 0")), (Cons, Nil, Ap, Integer)
    ).as_list
    data_list_2 = e.simplify(
        build_expression(tokenize("ap ap checkerboard 5 0")), (Cons, Nil, Ap, Integer)
    ).as_list

    screen.draw(t_list("ap ap vec 1 1"))
    screen.draw(
        t_list(
            "ap ap vec 5 3 , ap ap vec 6 3 , ap ap vec 4 4 , ap ap vec 6 4 , ap ap vec 4 5"
        )
    )
    screen.draw(data_list_1)
    screen.draw(data_list_2)

    # screen.draw([(1, 2), (2, 3)])
    # screen.draw([(15, 15), (12, 13)])
    # screen.draw([(51, 15), (12, 31)])
    # screen.draw([(31, 12), (52, 21)])
    # screen.draw([(41, 51), (56, 31)])
    # screen.draw([(21, 35), (22, 43)])

    screen.join()


if __name__ == "__main__":
    test_screen()
