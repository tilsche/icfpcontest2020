from zebv.screen import AlienScreen


def test_screen():
    screen = AlienScreen()
    screen.start()
    screen.draw([(1, 2), (2, 3)])
    screen.draw([(15, 15), (12, 13)])
    screen.join()


if __name__ == "__main__":
    test_screen()
