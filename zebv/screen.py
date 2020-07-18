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
        self.console = tcod.Console(WIDTH, HEIGHT)
        self.points = []

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

    def draw(self, points):
        self.points += points

    def clear(self):
        self.points = []

    def on_mouse_click(self, x, y):
        print(f"mouse click on ({x}, {y})")
