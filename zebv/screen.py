from threading import Thread

import tcod
from zebv.draw import ColorImg, Img

WIDTH, HEIGHT = 1, 1  # Console width and height in tiles.

PIXEL = 9565


class Coord(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y

    @property
    def as_galaxy(self):
        return self.x, self.y

    def as_tcod(self, offset: "Coord"):
        return self.x + offset.x, self.y + offset.y

    def __eq__(self, o):
        return self.x == o.x and self.y == o.y

    def __repr__(self):
        return f"{self.x} {self.y}"


class BoundingBox(object):
    def __init__(self):
        self.upper_left = Coord(0, 0)
        self.lower_right = Coord(0, 0)

    def add_point(self, point: Coord):
        if self.upper_left is None:
            self.upper_left = point
            self.lower_right = point
        else:
            self.upper_left = Coord(
                min(point.x, self.upper_left.x), min(point.y, self.upper_left.y)
            )
            self.lower_right = Coord(
                max(point.x, self.lower_right.x), max(point.y, self.lower_right.y)
            )

    def add_box(self, o: "BoundingBox"):
        self.add_point(o.lower_right)
        self.add_point(o.upper_left)

    @property
    def offset(self):
        return Coord(max(0, -self.upper_left.x), max(0, -self.upper_left.y))

    @property
    def size(self):
        return Coord(
            self.lower_right.x - self.upper_left.x + 1,
            self.lower_right.y - self.upper_left.y + 1,
        )


class Generation(object):
    def __init__(self):
        self.points = []
        self.bounding_box = BoundingBox()

    def add_point(self, point: Coord):
        self.points.append(point)
        self.bounding_box.add_point(point)

    def __iter__(self):
        return iter(self.points)


class AlienScreen(Thread):
    def __init__(self):
        super().__init__()
        self.tileset = tcod.tileset.load_tilesheet(
            "dejavu10x10_gs_tc.png", 32, 8, tcod.tileset.CHARMAP_TCOD,
        )
        self.clear()
        self.console = tcod.Console(WIDTH, HEIGHT)
        self.last_click = None

    def run(self):
        with tcod.context.new_terminal(
            self.console.width,
            self.console.height,
            title="🌌🌠🛸🌍🦓 Unicode support ftw?",
            tileset=self.tileset,
            vsync=True,
        ) as context:
            while True:
                self.console.clear()

                for generation, points in enumerate(reversed(self.generations)):
                    for point in points:
                        (x, y) = point.as_tcod(self.offset)
                        self.console.draw_rect(
                            x, y, 1, 1, fg=self.fg_color(generation), ch=PIXEL
                        )

                if self.last_click:
                    (x, y) = self.last_click
                    self.console.draw_rect(x, y, 1, 1, fg=(255, 0, 0), ch=PIXEL)

                context.present(self.console, keep_aspect=True)

                for event in tcod.event.wait():
                    context.convert_event(event)
                    if event.type == "MOUSEBUTTONDOWN":
                        x, y = event.tile
                        self.on_mouse_click(Coord(x - self.offset.x, y - self.offset.y))
                        self.last_click = (x, y)
                    if event.type == "QUIT":
                        raise SystemExit()

    @property
    def num_generations(self):
        return len(self.generations)

    def fg_color(self, generation):
        step = (255 // self.num_generations) * (generation + 1)
        return step, step, step

    @property
    def size(self):
        return self.bounding_box.size

    @property
    def offset(self):
        return self.bounding_box.offset

    def draw(self, nodes=[]):
        generation = Generation()

        for n in nodes:
            assert n.op.op == "cons"
            x = n.op.arg
            y = n.arg

            generation.add_point(Coord(x, y))

        self.generations.append(generation)
        self.bounding_box.add_box(generation.bounding_box)

        self.console = tcod.Console(self.size.x + 1, self.size.y + 1)

    def save(self, filename, interact_point: Coord):
        im = ColorImg(size=(self.size.x + 1, self.size.y + 1))

        for generation, points in enumerate(self.generations):
            for point in points:
                (x, y) = point.as_tcod(self.offset)
                im.add_point(x, y, color=self.fg_color(generation)[0])

        (x, y) = interact_point.as_tcod(self.offset)
        try:
            im.add_point(x, y, (255, 0, 0))
        except IndexError:
            pass

        im.save(filename)

    def clear(self):
        self.generations = []
        self.bounding_box = BoundingBox()
        self.bounding_box.add_point(Coord(-40, -40))
        self.bounding_box.add_point(Coord(40, 40))

    def on_mouse_click(self, point: Coord):
        print(f"mouse click on ({point.x}, {point.y})")
