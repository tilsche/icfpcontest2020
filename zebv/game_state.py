from typing import List, Tuple


class StaticGameInfo:
    def __init__(self, static_game_info):
        self.role: int

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
        self.ships_and_commands: List[Tuple[Ship, list]] = []
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
        self.position: Tuple[int, int]
        self.velocity: Tuple[int, int]

        self.role, ship = ship
        self.ship_id, ship = ship
        self.position, ship = ship
        self.velocity, ship = ship
        stats, ship = ship
        self.stats = ShipStats(stats)
        self.heat, ship = ship
        self.x6, ship = ship
        self.x7, ship = ship
        assert ship == ()

    def __repr__(self):
        return f"Ship (role: {self.role}, shipId: {self.ship_id}, position: {self.position}, velocity: {self.velocity}, stats: {self.stats}, heat: {self.heat}, x6: {self.x6}, x7: {self.x7})"


class ShipStats:
    def __init__(self, ship_stats):
        self.fuel, ship_stats = ship_stats
        self.shoot_power, ship_stats = ship_stats
        self.heat_reduction, ship_stats = ship_stats
        self.live_points, ship_stats = ship_stats
        assert () == ship_stats

    def __repr__(self):
        return f"Ship (fuel: {self.fuel}, shoot_power: {self.shoot_power}, heat_reduction: {self.heat_reduction}, live_points: {self.live_points}"


class GameResponse:
    def __init__(self, game_response):
        game_stage, game_response = game_response
        static_game_info, game_response = game_response
        game_state, game_response = game_response
        assert game_response == ()

        self.game_stage: int = game_stage
        self.static_game_info: StaticGameInfo = None
        self.game_state: GameState = None

        if self.game_stage in [0, 1]:
            self.static_game_info = StaticGameInfo(static_game_info)
        if self.game_stage in [1]:
            self.game_state = GameState(game_state)

    def __repr__(self):
        return f"GameResponse (game_stage: {self.game_stage}, static_game_info: {self.static_game_info}, game_state: {self.game_state})"


class LaserResponse:
    def __init__(self, resp):
        init_resp = resp
        resp, _ = resp
        resp, _ = resp
        self.command, resp = resp
        self.positon, resp = resp
        self.laser_power, resp = resp
        self.damage_delt, resp = resp
        self.x5, resp = resp
        if not (resp == ()):
            raise RuntimeError(
                f"Fecode of {init_resp} as LaserResponse failed: {resp} left over"
            )

    def __repr__(self):
        return f"LaserResponse (command: {self.command}, positon: {self.positon}, laser_power: {self.laser_power}, damage_delt: {self.damage_delt}, x5: {self.x5})"

