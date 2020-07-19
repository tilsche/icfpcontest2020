from threading import Thread, Lock

import tcod
from zebv.draw import ColorImg, Img

WIDTH, HEIGHT = 1, 1  # Console width and height in tiles.

PIXEL = 9565

SEARCH_RADIUS = 4


class Coord(object):
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y

    @classmethod
    def from_tcod(cls, point, offset: "Coord"):
        (x, y) = point
        return cls(x - offset.x, y - offset.y)

    @property
    def as_galaxy(self):
        return self.x, self.y

    def as_tcod(self, offset: "Coord"):
        return self.x + offset.x, self.y + offset.y

    def __eq__(self, o):
        return self.x == o.x and self.y == o.y

    def __repr__(self):
        return f"{self.x} {self.y}"

    def up(self) -> "Coord":
        return Coord(self.x, self.y - 1)

    def down(self) -> "Coord":
        return Coord(self.x, self.y + 1)

    def left(self) -> "Coord":
        return Coord(self.x - 1, self.y)

    def right(self) -> "Coord":
        return Coord(self.x + 1, self.y)


class BoundingBox(object):
    def __init__(self):
        self.upper_left = None
        self.lower_right = None

    def add_point(self, point: Coord):
        if point is None:
            return
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

    @property
    def xrange(self):
        yield from range(self.upper_left.x, self.lower_right.x + 1)

    @property
    def yrange(self):
        yield from range(self.upper_left.y, self.lower_right.y + 1)

    def __contains__(self, point: Coord):
        return point.x in self.xrange and point.y in self.yrange

    def __iter__(self):
        for y in self.yrange:
            for x in self.xrange:
                yield Coord(x, y)

    def __repr__(self):
        return f"[{self.upper_left} -- {self.lower_right}]"


class Generation(object):
    def __init__(self):
        self.points = []
        self.bounding_box = BoundingBox()

    def add_point(self, point: Coord):
        self.points.append(point)
        self.bounding_box.add_point(point)

    def __iter__(self):
        return iter(self.points)

    def __contains__(self, point: Coord):
        return point in self.points


class NumberFindyThingy(object):
    def __init__(self, points: Generation):
        self.points = points

    def __contains__(self, point: Coord):
        return point in self.points

    def parse_number(self, pivot: Coord, search_area: BoundingBox):
        if pivot in self:
            raise ValueError("Not a number")
        elif pivot.right() not in self or pivot.down() not in self:
            raise ValueError("Not a number")

        size = -1
        hrzt = vert = pivot

        is_neg = False

        while True:
            vert = vert.down()
            hrzt = hrzt.right()

            if hrzt in self and vert not in self:
                raise ValueError("Not a number")

            if hrzt not in self and vert in self:
                for _ in range(size + 1):
                    vert = vert.right()
                    if vert in self:
                        raise ValueError("Not a number")
                is_neg = True
                break

            if hrzt not in self and vert not in self:
                break

            size += 1

            if size > 7:
                raise ValueError("Not a number (seems to large)")

        number_area = BoundingBox()
        number_area.add_point(pivot.down().right())
        number_area.add_point(
            Coord(number_area.upper_left.x + size, number_area.upper_left.y + size)
        )

        number = 0
        for i, point in enumerate(number_area):
            if point in self:
                number += pow(2, i)

        if (size > 1 or (is_neg and size == 0)) and number == 0:
            raise ValueError("Not a number")

        parsed_number = []
        number_area.add_point(pivot)
        for point in number_area:
            if point in self:
                parsed_number.append(point)
        if is_neg:
            parsed_number.append(Coord(pivot.x, pivot.y + size + 2))

        return (
            -number if is_neg else number,
            parsed_number,
        )


class AlienScreen(Thread):
    def __init__(self):
        super().__init__()
        self.tileset = tcod.tileset.load_tilesheet(
            "dejavu10x10_gs_tc.png", 32, 8, tcod.tileset.CHARMAP_TCOD,
        )
        self.console = tcod.Console(WIDTH, HEIGHT)
        self.last_click = None
        self.mouse_pos = None
        self.parsed_number = None
        self.mutex = Lock()
        self.clear()

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

                with self.mutex:
                    for generation, points in enumerate(reversed(self.generations)):
                        color = self.fg_color(generation)
                        for point in points:
                            (x, y) = point.as_tcod(self.offset)
                            tcod.console_set_char_background(
                                self.console, x, y, color, tcod.BKGND_SET,
                            )

                if self.last_click:
                    (x, y) = self.last_click
                    self.console.draw_rect(x, y, 1, 1, fg=(255, 0, 0), ch=PIXEL)

                if self.mouse_pos:
                    (x, y) = self.mouse_pos
                    self.console.draw_rect(x, y, 1, 1, fg=(255, 255, 0), ch=PIXEL)

                if self.parsed_number:
                    for point in self.parsed_number:
                        (x, y) = point.as_tcod(self.offset)
                        tcod.console_set_char_background(
                            self.console, x, y, (255, 0, 255), tcod.BKGND_SET,
                        )

                context.present(self.console, keep_aspect=True)

                for event in tcod.event.wait():
                    context.convert_event(event)
                    if event.type == "MOUSEMOTION":
                        self.mouse_pos = event.tile

                    if (
                        event.type == "MOUSEBUTTONDOWN"
                        and event.button == tcod.event.BUTTON_LEFT
                    ):
                        with self.mutex:
                            self.on_mouse_click(
                                Coord.from_tcod(event.tile, self.offset)
                            )
                            self.last_click = (x, y)

                    if (
                        event.type == "MOUSEBUTTONDOWN"
                        and event.button == tcod.event.BUTTON_RIGHT
                    ):
                        with self.mutex:
                            self.find_number(Coord.from_tcod(event.tile, self.offset))

                    if event.type == "QUIT":
                        return

    def __contains__(self, point: Coord):
        for points in self.generations:
            for p in points:
                if point == p:
                    return True
        return False

    def find_number(self, point: Coord):
        search_area = BoundingBox()
        search_area.add_point(Coord(point.x - SEARCH_RADIUS, point.y - SEARCH_RADIUS))
        search_area.add_point(Coord(point.x + SEARCH_RADIUS, point.y + SEARCH_RADIUS))

        for generation in self.generations:
            finder = NumberFindyThingy(generation)
            for i in search_area.xrange:
                for j in search_area.yrange:
                    try:
                        (num, points) = finder.parse_number(Coord(i, j), search_area)
                        self.parsed_number = points
                        print(f"Parsed number: {num}")
                        return
                    except ValueError:
                        pass

        print(f"No number found")
        self.parsed_number = None

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
        with self.mutex:
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
        with self.mutex:
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
        with self.mutex:
            self.generations = []
            self.bounding_box = BoundingBox()
            self.bounding_box.add_point(Coord(-40, -40))
            self.bounding_box.add_point(Coord(40, 40))
            self.parsed_number = None

    def on_mouse_click(self, point: Coord):
        print(f"mouse click on ({point.x}, {point.y})")
