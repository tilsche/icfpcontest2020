import numpy as np
from PIL import Image

from . import node


class Img:
    def __init__(self, size):
        self._size = size
        self.pixels = np.zeros(self._size, np.uint8)

    def save(self, filename):
        self._img = Image.fromarray(self.pixels, mode="L")
        self._img.save(filename, format="png")


def draw(nodes=[], filename="", size=(1, 1)):
    points = []
    max_x = size[0]
    max_y = size[1]
    for n in nodes:
        assert n.op.op.name == "cons"
        y = n.op.arg
        x = n.arg
        points.append((x.value, y.value))
        max_x = max(x.value + 1, max_x)
        max_y = max(y.value + 1, max_y)

    new_size = (max_x, max_y)
    im = Img(new_size)

    for point in points:
        im.pixels[point] = 255

    if filename:
        im.save(filename)

    return im.pixels
