from zebv.screen import BoundingBox, Coord

import pytest


def test_bounding_box():
    bb = BoundingBox()
    null = Coord(0, 0)
    bb.add_point(null)

    assert bb.lower_right == null
    assert bb.upper_left == null
    assert bb.offset == null


def test_bounding_box1():
    bb = BoundingBox()
    null = Coord(0, 0)
    one = Coord(1, 1)
    bb.add_point(null)
    bb.add_point(one)

    assert bb.lower_right == one
    assert bb.upper_left == null
    assert bb.offset == null
    assert bb.size == Coord(2, 2)


def test_bounding_box2():
    bb = BoundingBox()
    null = Coord(0, 0)
    one = Coord(-1, -1)
    bb.add_point(null)
    bb.add_point(one)

    assert bb.lower_right == null
    assert bb.upper_left == one
    assert bb.offset == Coord(1, 1)
    assert bb.size == Coord(2, 2)


def test_bounding_box_combine():
    bb = BoundingBox()
    bb.add_point(Coord(0, 0))
    bb.add_point(Coord(-1, -1))

    bb2 = BoundingBox()
    bb2.add_point(Coord(0, 0))
    bb2.add_point(Coord(1, 1))

    bb.add_box(bb2)

    assert bb.lower_right == Coord(1, 1)
    assert bb.upper_left == Coord(-1, -1)
    assert bb.offset == Coord(1, 1)
    assert bb.size == Coord(3, 3)


@pytest.fixture
def bounding_box():
    bb = BoundingBox()
    bb.add_point(Coord(1, 1))
    bb.add_point(Coord(-1, -1))

    yield bb


def test_bounding_box_range(bounding_box):
    expected_points = [
        Coord(-1, -1),
        Coord(0, -1),
        Coord(1, -1),
        Coord(-1, 0),
        Coord(0, 0),
        Coord(1, 0),
        Coord(-1, 1),
        Coord(0, 1),
        Coord(1, 1),
    ]

    points = [point for point in bounding_box]

    assert len(points) == 9

    for actual, expected in zip(points, expected_points):
        assert actual == expected


def test_bounding_box_xrange(bounding_box):
    r = [i for i in bounding_box.xrange]
    assert [-1, 0, 1] == r


def test_bounding_box_yrange(bounding_box):
    r = [i for i in bounding_box.yrange]
    assert [-1, 0, 1] == r
