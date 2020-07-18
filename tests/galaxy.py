import sys

from zebv.interact import Interaction

sys.setrecursionlimit(50000)

data = open("galaxy").read().strip()

i = Interaction(data, "galaxy")
i(0, 0)
