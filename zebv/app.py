import logging

import click

import click_log

from .api import ApiClient
from .modem import demod, mod
from .game_state import GameResponse, LaserResponse
import zebv.calc as calc

import threading
import time
from math import pi
import collections

ATTAC = 0
DEFEND = 1


def lst(*items):
    """Generate a "tuple list"  from the list of arguments

    A tuple list is a sequence of tuples nested to the right, terminated by the
    empty tuple ().

    >>> lst()
    ()
    >>> lst(1)
    (1, ())
    >>> lst(1, 2, 3)
    (1, (2, (3, ())))
    """

    lst = ()
    for item in reversed(items):
        lst = (item, lst)
    return lst


class LogFormatter(logging.Formatter):
    colors = {
        "error": dict(fg="red"),
        "exception": dict(fg="red"),
        "critical": dict(fg="red"),
        "debug": dict(fg="blue"),
        "warning": dict(fg="yellow"),
        "info": dict(fg="green"),
    }

    def format(self, record: logging.LogRecord):
        level = record.levelname.lower()
        msg = record.getMessage()
        if level in self.colors:
            name_suffix = f"{record.name}:"
            prefix = click.style(f"{level}:{name_suffix} ", **self.colors[level])
            msg = "\n".join(prefix + x for x in msg.splitlines())
        return msg


handler = click_log.ClickHandler()
handler.formatter = LogFormatter()

logging.basicConfig(handlers=[handler])
# logging.basicConfig(level=logging.DEBUG)

logger = logging.getLogger(__name__)


DEGREE = 90

INIT_DIST_FAC = 2
DEG_MUL = 3


class Command:
    def __init__(self, client):
        self.client = client

    def _send(self, id_, *args):
        request = lst(id_, *args)
        logger.debug(
            f"=> Sending command {id_}: args={args} (rendered request: {request})"
        )

        modulated = mod(request)
        response = self.client.aliens_send(modulated)
        demodulated = demod(response)

        logger.debug(f"<= Received: {demodulated}")

        return demodulated

    def init(self):
        logger.debug("Sending INIT(1, 0)")
        status, result = self._send(1, 0)
        if status != 1:
            raise RuntimeError("Init Failed")

        (((_, (attac_player, _)), ((_, (def_player, _)), _)), _) = result
        return attac_player, def_player

    def join(self, player_key) -> GameResponse:
        # (2, playerKey, (...unknown list...))
        logger.debug(f"Sending JOIN(2, player_key={player_key}, (???))")
        status, result = self._send(2, player_key, ())
        if status != 1:
            raise RuntimeError(
                f"Join Failed: {player_key}, Response: {(status, result)}"
            )
        return result

    def start(self, player_key, ship_params=(1, 2, 3, 4)):
        ship_params = lst(*ship_params)
        logger.debug(
            f"Sending START(3, player_key={player_key}, ship_params={ship_params})"
        )
        status, result = self._send(3, player_key, ship_params)
        if status != 1:
            raise RuntimeError(
                f"Start Failed: {ship_params}, Response: {(status, result)}"
            )
        return result

    def command(self, player_key, *args):
        # (4, playerKey, (... ship commands? ...))
        logger.debug(
            f"Sending COMMAND(4, player_key={player_key}, args=({' '.join(map(str, args))}))"
        )
        status, result = self._send(4, player_key, lst(*args))
        if status != 1:
            raise RuntimeError(
                f"Failed to send COMMAND: {(args)} for player {player_key}, Response: {(status, result)}"
            )
        return result


class Player(threading.Thread):
    def __init__(self, player_key, command: Command, lock: threading.Lock):
        super().__init__()
        self._player_key = player_key
        self._command = command
        self.log = logger.getChild("PLAYER")
        self.game_response: GameResponse = None
        self.lock = lock

    def run(self):
        self.log.debug("Start")
        resp = self._command.join(self._player_key)
        self.act(resp)

    def act(self):
        pass

    def command(self, type_: int, *args) -> GameResponse:
        """Send player command of type `type_` with arguments `args`
        """
        response = self._command.command(self._player_key, lst(type_, *args))
        return GameResponse(response)

    def nothing(self):
        self.log.info(f"NOTHING()")
        response = self._command.command(self._player_key)
        return GameResponse(response)

    def accelerate(self, ship_id, vector=(0, 0)):
        """
        accelerates the ship in a direction opposit to vec.
        There seems to be a thermal budget, which defines the max boos a ship can do.

        @parma vec: needs to be between (-1,-1) and (1,1)
        """
        self.log.info(f"ACCELERATE(ship_id={ship_id}, vector={vector})")
        return self.command(0, ship_id, vector)

    def detonate(self, ship_id):
        self.log.info(f"DETONATE(ship_id={ship_id})")
        return self.command(1, ship_id)

    def shoot(self, ship_id, target, laser_power=()):
        self.log.info(
            f"SHOOT(ship_id={ship_id}, target={target}, laser_power={laser_power})"
        )
        return self.command(2, ship_id, target, laser_power)


class AttacPlayer(Player):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.log = logger.getChild(f"ATTAC  ({ATTAC})")
        self.log.info(f"Player Key: {self._player_key}")
        self.previous_target_movements = collections.defaultdict(list)
        # self._ship_params = (10, 10, 10, 10)
        # (fuel, shot_power, heat_reduction, live_points)
        # treffer und schüsse reduzieren head_cap
        # wenn heat_cap aufgebraucht:
        # * schüsse
        #   * reduzieren shot_power
        #   * wenn shoot power leer ist --> angreifer tot
        # * treffer
        #   * reduzieren shield
        #   * wenn shield leer -->  live_points werden reduziert
        #   * wenn live_points leer --> verteidiger tot

        self._ship_params = (62, 64, 16, 1)  # copy&paste unagi

    def act(self, resp):
        self.game_response = GameResponse(resp)
        self.log.info(f"Start as {self.game_response.static_game_info.role} == {ATTAC}")
        resp = self._command.start(self._player_key, self._ship_params)
        self.game_response = self.nothing()

        inital_distance = None
        degree = DEGREE
        shoot = False

        while self.game_response.game_stage == 1:
            s_u_c = self.game_response.game_state.ships_and_commands.ships_and_commands
            for (ship, commands) in s_u_c:
                if ship.role == DEFEND:
                    self.previous_target_movements[ship.ship_id].append(ship)
                    self.log.info(f"Opponent defend ship: {ship}, {commands}")
                if ship.role == ATTAC:
                    self.log.info(f"my attac ship:        {ship}, {commands}")
                    self.lock.acquire()
                    self.log.info(
                        f"Tick:     {self.game_response.game_state.game_tick}"
                    )
                    self.log.info(
                        f"Distance: {calc.distance(ship.position)}, Degree: {degree}"
                    )

                    laser_response = None
                    try:
                        laser_response = LaserResponse(commands)

                    except (RuntimeError, ValueError) as e:
                        self.log.warn(f"Cannot decond Command:  {commands}, {e}")
                        pass
                    self.log.info(f"Laser Response: {laser_response}")

                    self.lock.release()

                    if not inital_distance:
                        inital_distance = calc.distance(ship.position)

                    current_distance = calc.distance(ship.position)

                    if ship.heat >= 64:  # do nothing with wo much heat
                        self.log.info(f"FALL BACK {ship.ship_id} AND NO SHOOT")
                        self.game_response = self.nothing()
                    elif shoot:
                        shoot = False
                        self.game_response = self.cause_shoot(ship, s_u_c)
                    else:
                        shoot = True
                        diff = current_distance - inital_distance
                        degree += DEG_MUL * ((diff) / inital_distance) ** INIT_DIST_FAC
                        self.log.info(
                            f"Distance: {calc.distance(ship.position)}, New Degree: {degree}, Diff: {((diff) / inital_distance)} "
                        )
                        rad = calc.rad(degree)
                        self.log.info(f"rad = {rad} ({degree})")
                        vec = calc.orbit(ship, rad)

                        self.log.info(f"ACCELERATE {ship.ship_id}, VEC: {vec}")
                        self.game_response = self.accelerate(ship.ship_id, vec)

                    # self.game_response = self.detonate(ship.ship_id)
                    #
                    # self.game_response = self.shoot(ship.ship_id, (1, 1), 1)

        self.log.info(f"Finished: {self.game_response}")

    def cause_shoot(self, ship, s_u_c):
        for (other_ship, commands) in s_u_c:
            if other_ship.role == DEFEND:  # attac the defenderrs XD
                shoot_to = calc.shoot_direction(
                    ship,
                    other_ship,
                    self.previous_target_movements[other_ship.ship_id],
                )
                self.log.info(
                    f"SHOOT TO {other_ship.ship_id}, at {other_ship.position}, with {shoot_to}"
                )
                return self.shoot(ship.ship_id, shoot_to, 1)


class DefendPlayer(Player):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.log = logger.getChild(f"DEFEND ({DEFEND})")
        self.log.info(f"Player Key: {self._player_key}")
        # self._ship_params = (10, 10, 10, 10)
        self._ship_params = (208, 0, 4, 96)  # copy&paste unagi

    def act(self, resp):
        self.game_response = GameResponse(resp)
        self.log.info(
            f"Start as {self.game_response.static_game_info.role} == {DEFEND}"
        )
        resp = self._command.start(self._player_key, self._ship_params)
        self.game_response = self.nothing()

        inital_distance = None
        degree = DEGREE
        while self.game_response.game_stage == 1:
            # self.log.info(self.game_response)
            # tic_toc = not tic_toc
            # if not tic_toc:
            #    self.nothing()
            #    continue

            s_u_c = self.game_response.game_state.ships_and_commands.ships_and_commands

            for (ship, commands) in s_u_c:
                if ship.role == ATTAC:
                    self.log.info(f"Opponent attac ship: {ship}")
                if ship.role == DEFEND:
                    self.log.info(f"my defend ship:      {ship}")
                    self.lock.acquire()
                    self.log.info(
                        f"Tick:     {self.game_response.game_state.game_tick}"
                    )
                    self.log.info(
                        f"Distance: {calc.distance(ship.position)}, Degree: {degree}"
                    )
                    self.log.info(f"Commands: {commands}")
                    self.log.info(f"Ship stats: {ship}")

                    self.lock.release()

                    if not inital_distance:
                        inital_distance = calc.distance(ship.position)

                    current_distance = calc.distance(ship.position)

                    if ship.heat >= 64:  # do nothing with wo much heat
                        self.log.info(f"FALL BACK {ship.ship_id} AND NO SHOOT")
                        self.game_response = self.nothing()

                    else:
                        diff = current_distance - inital_distance
                        degree += DEG_MUL * ((diff) / inital_distance) ** INIT_DIST_FAC
                        self.log.info(
                            f"Distance: {calc.distance(ship.position)}, New Degree: {degree}, Diff: {((diff) / inital_distance)} "
                        )
                        rad = calc.rad(degree)
                        self.log.info(f"rad = {rad} ({degree})")
                        vec = calc.orbit(ship, rad)

                        self.log.info(f"ACCELERATE {ship.ship_id}, VEC: {vec}")
                        self.game_response = self.accelerate(ship.ship_id, vec)
                    # self.game_response = self.detonate(ship.ship_id)
                    #
                    # self.game_response = self.shoot(ship.ship_id, (1, 1), 1)

        self.log.info(f"Finished: {self.game_response}")


@click.command()
@click.argument("server_url")
@click.argument("player_key", type=int)
@click.option("-k", "--api-key", default=None)
@click_log.simple_verbosity_option(logger)
def main(server_url, player_key, api_key):
    logger.info("ServerUrl: %s; PlayerKey: %s" % (server_url, player_key))

    client = ApiClient(server_url, api_key)
    # resp = client.aliens_send("data")
    # print(resp)

    # request = Ap(Ap(Cons(), Number(2)), Ap(Ap(Cons(), Number(int(player_key))), Nil()))

    command = Command(client)

    if player_key == 0:  # Testcase, not for submission
        logger.info("Choose Testing Mode")
        lock = threading.Lock()
        attac_player_key, defend_player_key = command.init()
        attac = AttacPlayer(attac_player_key, command, lock)
        defend = DefendPlayer(defend_player_key, command, lock)
        attac.start()
        defend.start()

    else:
        logger.info("Choose Submission Mode")
        resp = command.join(player_key)
        game_resp = GameResponse(resp)
        player = None

        if game_resp.game_stage in [0, 1]:
            logger.info("Start Game")
            if game_resp.static_game_info.role == 0:
                lock = threading.Lock()
                player = AttacPlayer(player_key, command, lock)
            elif game_resp.static_game_info.role == 1:
                lock = threading.Lock()
                player = DefendPlayer(player_key, command, lock)
            else:
                raise RuntimeError(f"Unkone role {game_resp.static_game_info.role}")

            player.act(resp)
        else:
            logger.info(f"Game finished ({game_resp.game_stage})")


if __name__ == "__main__":
    main()
