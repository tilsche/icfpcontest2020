import numpy as np
from PIL import Image


class Img:
    def __init__(self, size):
        self._size = size
        self.pixels = np.zeros(self._size, np.uint8)

    def add_point(self, x, y, color=255):
        self.pixels[(x, y)] = color

    def save(self, filename):
        self._img = Image.fromarray(np.transpose(self.pixels), mode="L")
        self._img.save(filename, format="png")


class ColorImg:
    def __init__(self, size):
        self._size = size
        self.pixels = np.full(self._size, 0xFF << 24, np.uint32)

    def add_point(self, x, y, color=255):
        if isinstance(color, int):
            color = (color, color, color)

        color = (color[0] << 0) | (color[1] << 8) | (color[2] << 16) | (0xFF << 24)
        self.pixels[(x, y)] = color

    def save(self, filename):
        self._img = Image.fromarray(np.transpose(self.pixels), mode="RGBA")
        self._img.save(filename, format="png")


def draw(nodes=[], filename="", size=(1, 1)):
    points = []
    max_x = size[0]
    max_y = size[1]
    for n in nodes:
        assert n.op.op == "cons"
        x = n.op.arg
        y = n.arg
        points.append((x, y))
        max_x = max(x + 1, max_x)
        max_y = max(y + 1, max_y)

    new_size = (max_x, max_y)
    im = Img(new_size)

    for point in points:
        im.add_point(*point)

    if filename:
        im.save(filename)

    return im.pixels


def draw_sub_image(*args, **kwargs):
    return draw(*args, **kwargs)


def multipledraw(nodes, filename=""):
    pic = Picture
    for node in nodes:
        pic.draw(node.as_list)
    if filename:
        pic.save(filename)


class Picture:
    def __init__(self, size=(1, 1)):
        self._size_x = size[0]
        self._size_y = size[1]

        self._pixels = np.zeros(size, np.uint8)
        self._current_x = 0
        self._current_y = 0
        self._border = 2

    def draw(self, nodes=[], size=(1, 1)):
        sub_pixels = draw(nodes, size=size)
        (sub_x, sub_y) = sub_pixels.shape

        self._size_x = max(sub_x + self._current_x + self._border, self._size_x)
        self._size_y = max(sub_y + self._current_y + self._border, self._size_y)

        self._pixels.resize((self._size_x + 2, self._size_y + 2))
        self._pixels[
            self._current_x + self._border : self._current_x + self._border + sub_x,
            self._current_y + self._border : self._current_y + self._border + sub_y,
        ] = sub_pixels

        self._current_x = self._current_x + self._border + sub_x
        # no check for linebreaks yet, self.current_y stays 0
        # self._current_y = self._current_y + self._border + sub_y

    def save(self, filename=""):
        self._img = Image.fromarray(np.transpose(self._pixels), mode="L")
        print(filename)
        self._img.save(filename, format="png")
