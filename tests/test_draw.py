import pytest
import zebv.draw as draw
import zebv.parsing as parsing


def t(exp):
    return parsing.build_expression(parsing.tokenize(exp))


def t_list(vecs):
    res = []
    for v in vecs.split(","):
        res.append(t(v))
    return res


def test_draw_1():
    draw.draw()


def test_draw_2():
    draw.draw(t_list("ap ap vec 1 1"))


def test_draw_3():
    draw.draw(t_list("ap ap vec 1 2"))


def test_draw_4():
    draw.draw(t_list("ap ap vec 2 5"))


def test_draw_5():
    draw.draw(t_list("ap ap vec 1 2 , ap ap vec 3 1 "))


def test_draw_6():
    draw.draw(
        t_list(
            "ap ap vec 5 3 , ap ap vec 6 3 , ap ap vec 4 4 , ap ap vec 6 4 , ap ap vec 4 5"
        )
    )


if __name__ == "__main__":
    test_draw_6()
