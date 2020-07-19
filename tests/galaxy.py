import sys

from zebv.interact import Interaction

sys.setrecursionlimit(50000)

data = open("galaxy").read().strip()

i = Interaction(data, "galaxy", interactive=True)
i(0, 0)
i(0, 0)
i(0, 0)
i(0, 0)
i(0, 0)
i(0, 0)
i(0, 0)
i(0, 0)

i(0, 0)
i(8, 4)
i(2, -8)
i(3, 6)
i(0, -14)
i(-4, 10)
i(9, -3)
i(-4, 10)
i(1, 4)

i.run()
