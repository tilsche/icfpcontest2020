from . import node
from PIL import Image
import numpy as np

class Img:
    def __init__(self):
        self._size = (13,17)
        self.pixels = np.zeros(self._size, np.uint8)


    def save(self, filename):
        self._img = Image.fromarray(self.pixels, mode="L")
        self._img.save(filename, format="png")


def draw(nodes = [], filename = "test.png"):
    im = Img()
    for n in nodes:
        assert n.op.op.name == "vec"
        y = n.op.arg
        x = n.arg
        im.pixels[x.value,y.value] = 255
    print(im.pixels)
    im.save(filename)
        #im.pixels