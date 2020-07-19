from zebv.eval import Evaluator
from zebv.expression import as_list, build_expression
from zebv.screen import AlienScreen, Coord


def t(exp):
    return build_expression(exp)


def t_list(vecs):
    res = []
    for v in vecs.split(","):
        res.append(t(v))
    return res


# GALAXY = "ap ap cons ap ap cons ap ap cons -1 -3 ap ap cons ap ap cons 0 -3 ap ap cons ap ap cons 1 -3 ap ap cons ap ap cons 2 -2 ap ap cons ap ap cons -2 -1 ap ap cons ap ap cons -1 -1 ap ap cons ap ap cons 0 -1 ap ap cons ap ap cons 3 -1 ap ap cons ap ap cons -3 0 ap ap cons ap ap cons -1 0 ap ap cons ap ap cons 1 0 ap ap cons ap ap cons 3 0 ap ap cons ap ap cons -3 1 ap ap cons ap ap cons 0 1 ap ap cons ap ap cons 1 1 ap ap cons ap ap cons 2 1 ap ap cons ap ap cons -2 2 ap ap cons ap ap cons -1 3 ap ap cons ap ap cons 0 3 ap ap cons ap ap cons 1 3 nil ap ap cons ap ap cons ap ap cons -7 -3 ap ap cons ap ap cons -8 -2 nil ap ap cons nil nil"
GALAXY = "ap ap cons ap ap cons ap ap cons 0 -12 ap ap cons ap ap cons 0 -13 ap ap cons ap ap cons 0 -14 ap ap cons ap ap cons 0 -15 ap ap cons ap ap cons 0 -16 ap ap cons ap ap cons 0 -17 ap ap cons ap ap cons 0 -18 ap ap cons ap ap cons 0 -19 ap ap cons ap ap cons 0 -20 ap ap cons ap ap cons 0 -21 ap ap cons ap ap cons 0 -22 ap ap cons ap ap cons 0 -23 ap ap cons ap ap cons 0 -24 ap ap cons ap ap cons 0 -25 ap ap cons ap ap cons 0 -26 ap ap cons ap ap cons 0 -27 nil ap ap cons nil ap ap cons ap ap cons ap ap cons 10 -14 ap ap cons ap ap cons 9 -14 ap ap cons ap ap cons 8 -14 ap ap cons ap ap cons 7 -14 ap ap cons ap ap cons 6 -14 ap ap cons ap ap cons 5 -14 ap ap cons ap ap cons 4 -14 ap ap cons ap ap cons 3 -14 ap ap cons ap ap cons 2 -14 ap ap cons ap ap cons 1 -14 ap ap cons ap ap cons 0 -14 ap ap cons ap ap cons -1 -14 ap ap cons ap ap cons -2 -14 ap ap cons ap ap cons -3 -14 ap ap cons ap ap cons -4 -14 ap ap cons ap ap cons -5 -14 nil nil"


def test_screen():
    screen = AlienScreen()
    screen.start()

    e = Evaluator()
    # data_list_1 = e.simplify(
    #     build_expression(tokenize("ap ap checkerboard 7 0")), (Cons, Nil, Ap, Integer)
    # ).as_list
    # data_list_2 = e.simplify(
    #     build_expression(tokenize("ap ap checkerboard 5 0")), (Cons, Nil, Ap, Integer)
    # ).as_list
    #
    # screen.draw(t_list("ap ap vec 1 1"))
    # screen.draw(
    #     t_list(
    #         "ap ap vec 5 3 , ap ap vec 6 3 , ap ap vec 4 4 , ap ap vec 6 4 , ap ap vec 4 5"
    #     )
    # )
    #
    # screen.draw(data_list_1)
    # screen.draw(data_list_2)

    # screen.draw([(1, 2), (2, 3)])
    # screen.draw([(15, 15), (12, 13)])
    # screen.draw([(51, 15), (12, 31)])
    # screen.draw([(31, 12), (52, 21)])
    # screen.draw([(41, 51), (56, 31)])
    # screen.draw([(21, 35), (22, 43)])

    galaxy = as_list(e.eval(build_expression(GALAXY)))

    for list in galaxy:
        screen.draw(as_list(list))

    screen.save("test.png", Coord(0, 0))

    screen.join()


if __name__ == "__main__":
    test_screen()
