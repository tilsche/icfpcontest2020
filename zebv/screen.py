from threading import Thread

import tcod
from zebv.draw import Img

WIDTH, HEIGHT = 1, 1  # Console width and height in tiles.

PIXEL = 9565


class AlienScreen(Thread):
    def __init__(self):
        super().__init__()
        self.tileset = tcod.tileset.load_tilesheet(
            "dejavu10x10_gs_tc.png", 32, 8, tcod.tileset.CHARMAP_TCOD,
        )
        self._max_x = WIDTH
        self._max_y = HEIGHT
        self.console = tcod.Console(self._max_x, self._max_y)
        self.generations = []
        self.offset_x = 0
        self.offset_y = 0

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

                for generation, points in enumerate(self.generations):
                    for (x, y) in points:
                        self.console.draw_rect(
                            x, y, 1, 1, fg=self.fg_color(generation), ch=PIXEL
                        )

                context.present(self.console, keep_aspect=True)

                for event in tcod.event.wait():
                    context.convert_event(event)
                    if event.type == "MOUSEBUTTONDOWN":
                        x, y = event.tile
                        self.on_mouse_click(x - self.offset_x, y - self.offset_y)
                    if event.type == "QUIT":
                        raise SystemExit()

    @property
    def num_generations(self):
        return len(self.generations)

    def fg_color(self, generation):
        step = (255 // self.num_generations) * (generation + 1)
        return (step, step, step)

    def update_offset(self, offset_x, offset_y):
        new_generations = []
        for points in self.generations:
            new_points = []
            for (x, y) in points:
                new_points.append(
                    (x - self.offset_x + offset_x, y - self.offset_y + offset_y)
                )
                self._max_x = max(x - self.offset_x + offset_x + 1, self._max_x)
                self._max_y = max(y - self.offset_y + offset_y + 1, self._max_y)

            new_generations.append(new_points)
        self.generations = new_generations
        self.offset_x = offset_x
        self.offset_y = offset_y

    def draw(self, nodes=[]):
        points = []
        offset_x = 0
        offset_y = 0

        for n in nodes:
            assert n.op.op == "cons"
            x = n.op.arg
            y = n.arg
            points.append((x + self.offset_x, y + self.offset_y))
            offset_x = min(x, offset_x)
            offset_y = min(y, offset_y)

        self.generations.append(points)

        offset_x = -offset_x
        offset_y = -offset_y
        if offset_x > self.offset_x or offset_y > self.offset_y:
            self.update_offset(offset_x, offset_y)

        self.console = tcod.Console(self._max_x, self._max_y)

    def save(self, filename):
        im = Img(size=(self._max_x, self._max_y))

        for generation, points in enumerate(self.generations):
            for (x, y) in points:
                im.add_point(x, y, color=self.fg_color(generation)[0])

        im.save(filename)

    def clear(self):
        self.generations = []

    def on_mouse_click(self, x, y):
        print(f"mouse click on ({x}, {y})")
