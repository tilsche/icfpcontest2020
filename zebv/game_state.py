class StaticGameInfo:
    def __init__(self, static_game_info):
        self.x0, static_game_info = static_game_info
        self.role, static_game_info = static_game_info
        self.x2, static_game_info = static_game_info
        self.x3, static_game_info = static_game_info
        self.x4, static_game_info = static_game_info
        assert static_game_info == ()

    def __repr__(self):
        return f"StaticGameInfo (x0: {self.x0}, role: {self.role}, x2: {self.x2}, x3: {self.x3}, x4: {self.x4})"


class GameState:
    def __init__(self, game_state):
        self.game_tick, game_state = game_state
        self.x1, game_state = game_state
        ships_and_commands, game_state = game_state
        self.ships_and_commands = ShipsAndCommands(ships_and_commands)
        assert game_state == ()

    def __repr__(self):
        return f"GameState (game_tick: {self.game_tick}, x1: {self.x1}, ships_and_commands: {self.ships_and_commands})"


class ShipsAndCommands:
    def __init__(self, ships_and_commands):
        self.ships_and_commands = []
        while True:
            if ships_and_commands == ():
                break
            else:
                s, ships_and_commands = ships_and_commands
                ship, applied_commands = s
                self.ships_and_commands.append((Ship(ship), applied_commands))

    def __repr__(self):
        return f"ShipsAndCommands ({self.ships_and_commands})"


class Ship:
    def __init__(self, ship):
        self.role, ship = ship
        self.ship_id, ship = ship
        self.position, ship = ship
        self.velocity, ship = ship
        self.x4, ship = ship
        self.x5, ship = ship
        self.x6, ship = ship
        self.x7, ship = ship
        assert ship == ()

    def __repr__(self):
        return f"Ship (role: {self.role}, shipId: {self.ship_id}, position: {self.position}, velocity: {self.velocity}, x4: {self.x4}, x5: {self.x5}, x6: {self.x6}, x7: {self.x7})"


class GameResponse:
    def __init__(self, game_response):
        game_stage, game_response = game_response
        static_game_info, game_response = game_response
        game_state, game_response = game_response
        assert game_response == ()

        self.game_stage = game_stage
        self.static_game_info = ()
        self.game_state = ()

        if self.game_stage in [0, 1]:
            self.static_game_info = StaticGameInfo(static_game_info)
        if self.game_stage in [1]:
            self.game_state = GameState(game_state)

    def __repr__(self):
        return f"GameResponse (game_stage: {self.game_stage}, static_game_info: {self.static_game_info}, game_state: {self.game_state})"
