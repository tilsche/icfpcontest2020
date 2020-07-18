import pytest

import zebv.draw as draw
from zebv import patterns
from zebv.eval import Evaluator
from zebv.node import Ap, Number
from zebv.operators import Cons, Nil
from zebv.parsing import build_expression, tokenize

import numpy as np

def t(exp):
    return build_expression(tokenize(exp))


def t_list(vecs):
    res = []
    for v in vecs.split(","):
        res.append(t(v))
    return res


def test_draw_1():
    s = (13,17)
    exp = np.zeros(s)
    ret = draw.draw(size=s)
    assert (exp == ret).all()


def test_draw_2():
    s = (13,17)
    exp = np.zeros(s)
    exp[1,1] = 255
    ret = draw.draw(t_list("ap ap vec 1 1"), size=s)
    assert (exp == ret).all()

def test_draw_3():
    s = (13,17)
    exp = np.zeros(s)
    exp[2,1] = 255
    ret = draw.draw(t_list("ap ap vec 1 2"), size=s)
    assert (exp == ret).all()


def test_draw_4():
    s = (13,17)
    exp = np.zeros(s)
    exp[5,2] = 255
    ret = draw.draw(t_list("ap ap vec 2 5"), size=s)
    assert (exp == ret).all()


def test_draw_5():
    s = (13,17)
    exp = np.zeros(s)
    exp[2,1] = 255
    exp[1,3] = 255
    ret = draw.draw(t_list("ap ap vec 1 2 , ap ap vec 3 1 "), size=s)
    assert (exp == ret).all()


def test_draw_6():
    s = (13,17)    
    exp = np.zeros(s)
    exp[3,5] = 255
    exp[3,6] = 255
    exp[4,4] = 255
    exp[4,6] = 255
    exp[5,4] = 255
    ret = draw.draw(
        t_list(
            "ap ap vec 5 3 , ap ap vec 6 3 , ap ap vec 4 4 , ap ap vec 6 4 , ap ap vec 4 5"
        ),
        size=s
    )
    assert (exp == ret).all()

def np_checkboard(size):
    exp = np.zeros(size)
    for i in range(size[0]):
        for j in range(size[1]):
            field = (((i+1)%2) + j%2)%2
            exp[i,j] = field * 255
    return exp



def test_checkerboard_1():
    e = Evaluator()
    data_list = e.simplify(
        build_expression(tokenize("ap ap checkerboard 7 0")), (Cons, Nil, Ap, Number)
    ).as_list
    ret = draw.draw(data_list.get(), "checkerboard_1.png")
    exp = np_checkboard((7,7))
    assert (exp == ret).all()


    
def test_checkerboard_2():
    #s = (13,17)    
    e = Evaluator()
    data_list = e.simplify(
        build_expression(tokenize("ap ap checkerboard 13 0")), (Cons, Nil, Ap, Number)
    ).as_list
    ret = draw.draw(data_list.get(), "checkerboard_2.png")
    exp = np_checkboard((13,13))
    assert (exp == ret).all()



if __name__ == "__main__":
    test_checkerboard_2()
