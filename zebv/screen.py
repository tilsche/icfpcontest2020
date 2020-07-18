from threading import Thread

import tcod

WIDTH, HEIGHT = 20, 20  # Console width and height in tiles.

PIXEL = 9565


class AlienScreen(Thread):
    def __init__(self):
        super().__init__()
        self.tileset = tcod.tileset.load_tilesheet(
            "dejavu10x10_gs_tc.png", 32, 8, tcod.tileset.CHARMAP_TCOD,
        )
        # Create the main console.
        self._max_x = WIDTH
        self._max_y = HEIGHT
        self.console = tcod.Console(self._max_x, self._max_y)
        self.generations = []

    def run(self):
        with tcod.context.new_terminal(
            self.console.width,
            self.console.height,
            title="🌌🌠🛸🌍🦓 Unicode support ftw?",
            tileset=self.tileset,
        ) as context:
            while True:
                self.console.clear()

                for age, generation in enumerate(self.generations):
                    for (x, y) in generation:
                        self.console.draw_rect(
                            x, y, 1, 1, fg=self.fg_color(age), ch=PIXEL
                        )

                context.present(self.console, keep_aspect=True)

                for event in tcod.event.wait():
                    context.convert_event(event)
                    if event.type == "MOUSEBUTTONDOWN":
                        self.on_mouse_click(*event.tile)
                    if event.type == "QUIT":
                        raise SystemExit()

    @property
    def num_generations(self):
        return len(self.generations)

    def fg_color(self, generation):
        step = (255 // self.num_generations) * (generation + 1)
        return (step, step, step)

    def draw(self, nodes=[]):
        points = []
        for n in nodes:
            assert n.op.op.name == "cons"
            x = n.op.arg
            y = n.arg
            points.append((x.value, y.value))
            self._max_x = max(x.value + 1, self._max_x)
            self._max_y = max(y.value + 1, self._max_y)

        self.console = tcod.Console(self._max_x, self._max_y)
        self.generations.append(points)

    def clear(self):
        self.points = []

    def on_mouse_click(self, x, y):
        print(f"mouse click on ({x}, {y})")
