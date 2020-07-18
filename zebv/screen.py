from threading import Thread

import tcod

WIDTH, HEIGHT = 80, 60  # Console width and height in tiles.


class AlienScreen(Thread):
    def __init__(self):
        super().__init__()
        # Load the font, a 64 by 8 tile font with libtcod's old character layout.
        self.tileset = tcod.tileset.load_tilesheet(
            "dejavu10x10_gs_tc.png", 32, 8, tcod.tileset.CHARMAP_TCOD,
        )
        # Create the main console.
        self.console = tcod.Console(WIDTH, HEIGHT)
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
                    self.console.put_char(x, y, ch=75)

                context.present(self.console)

                for event in tcod.event.wait():
                    context.convert_event(event)
                    # print(event)
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

    def clean(self):
        self.points = []
