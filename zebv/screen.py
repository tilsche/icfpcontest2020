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
        self.console = tcod.Console(self._max_x, self._max_y)
        self.points = []
        self._max_x = 20
        self._max_y = 20

    def run(self):
        with tcod.context.new_terminal(
            self.console.width,
            self.console.height,
            title="🌌🌠🛸🌍🦓 Unicode support ftw?",
            tileset=self.tileset,
        ) as context:
            while True:
                self.console.clear()

                for (x, y) in self.points:
                    self.console.draw_rect(x, y, 1, 1, ch=PIXEL)

                context.present(self.console, keep_aspect=True)

                for event in tcod.event.wait():
                    context.convert_event(event)
                    if event.type == "MOUSEBUTTONDOWN":
                        self.on_mouse_click(*event.tile)
                    if event.type == "QUIT":
                        raise SystemExit()

    def draw(self, nodes=[]):
        points = []
        for n in nodes:
            assert n.op.op.name == "cons"
            x = n.op.arg
            y = n.arg
            points.append((x.value, y.value))
            self._max_x = max(x.value + 1, self._max_x)
            self._max_y = max(y.value + 1, self._max_y)

    def clear(self):
        self.points = []

    def on_mouse_click(self, x, y):
        print(f"mouse click on ({x}, {y})")
