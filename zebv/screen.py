import tcod

from threading import Thread

WIDTH, HEIGHT = 80, 60  # Console width and height in tiles.


class AlienScreen(Thread):
    def __init__(self):
        super().__init__()
        # Load the font, a 64 by 8 tile font with libtcod's old character layout.
        self.tileset = tcod.tileset.load_tilesheet(
            "dejavu10x10_gs_tc.png", 64, 8, tcod.tileset.CHARMAP_TCOD,
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
                    self.console.put_char(x, y, ch=75)

                context.present(self.console)

                for event in tcod.event.wait():
                    context.convert_event(event)
                    # print(event)
                    if event.type == "QUIT":
                        raise SystemExit()

    def draw(self, points):
        self.points += points

    def clean(self):
        self.points = []
