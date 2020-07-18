from zebv.interact import Interaction


def test_interaction(statefuldraw):
    i = Interaction(statefuldraw, "statefuldraw")
    i(4, 8)
    i(7, 7)
    i(12, 14)
