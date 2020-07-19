from zebv.screen import BoundingBox, Coord


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
