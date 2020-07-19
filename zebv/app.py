import logging

import click

import click_log

from .api import ApiClient
from .modem import demod, mod
from .game_state import GameResponse

import threading
import time

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
    def __init__(self, player_key, command: Command):
        super().__init__()
        self._player_key = player_key
        self._command = command
        self.log = logger.getChild("PLAYER")
        self.game_response: GameResponse = None

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
        # debug:zebv.app: => (4, (7981600807349721590, ((), ()))) ~~~~~> (send)
        #                   (4, (4471937984043146841, ((), ())))
        #                   (4, (4471937984043146841, ((), ()))), ())

        self.log.info(f"NOTHING()")
        response = self._command.command(self._player_key)
        return GameResponse(response)

    def accelerate(self, ship_id, vector=(0, 0)):
        self.log.info(f"ACCELERATE(ship_id={ship_id}, vector={vector})")
        return self.command(0, ship_id, vector)

    def detonate(self, ship_id):
        self.log.info(f"DETONATE(ship_id={ship_id})")
        return self.command(1, ship_id)

    def shoot(self, ship_id, target, x3=()):
        self.log.info(f"SHOOT(ship_id={ship_id}, target={target}, ?x3={x3})")
        return self.command(2, ship_id, target, x3)


class AttacPlayer(Player):
    def __init__(self, player_key, command, log_level=logging.ERROR):
        super().__init__(player_key, command)
        self.log = logger.getChild(f"ATTAC ({ATTAC})")
        self.log.setLevel(log_level)
        self.log.info(f"Player Key: {self._player_key}")
        self._ship_params = (1, 2, 3, 4)

    def act(self, resp):
        self.game_response = GameResponse(resp)
        self.log.info(f"Start as {self.game_response.static_game_info.role} == {ATTAC}")
        resp = self._command.start(self._player_key, self._ship_params)
        self.game_response = self.nothing()

        while self.game_response.game_stage == 1:
            self.log.info(self.game_response)
            s_u_c = self.game_response.game_state.ships_and_commands.ships_and_commands
            for (ship, commands) in s_u_c:
                if ship.role == ATTAC:
                    self.log.info(f"NOTHING {ship.ship_id}")
                    resp = self.nothing()
                    self.game_response = resp

        self.log.info(f"Finished: {self.game_response}")


class DefendPlayer(Player):
    def __init__(self, player_key, command, log_level=logging.DEBUG):
        super().__init__(player_key, command)
        self.log = logger.getChild(f"DEFEND {DEFEND}")
        self.log.info(f"Player Key: {self._player_key}")
        self._ship_params = (1, 2, 3, 4)

    def act(self, resp):
        self.game_response = GameResponse(resp)
        self.log.info(
            f"Start as {self.game_response.static_game_info.role} == {DEFEND}"
        )
        resp = self._command.start(self._player_key, self._ship_params)
        self.game_response = self.nothing()

        inital_pos = None
        while self.game_response.game_stage == 1:
            # self.log.info(self.game_response)
            s_u_c = self.game_response.game_state.ships_and_commands.ships_and_commands
            for (ship, commands) in s_u_c:
                if ship.role == DEFEND:
                    self.log.info(f"position: {ship.position}, vel: {ship.velocity}")
                    if not inital_pos:
                        inital_pos = ship.position
                    xi, yi = inital_pos
                    x, y = ship.position
                    fac = 2
                    vec = (fac * (x - xi), fac * (y - yi))
                    #vec = (1, 1)
                    self.log.info(f"ACCELERATE {ship.ship_id}, VEC: {vec}")
                    self.game_response = self.accelerate(ship.ship_id, vec)
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
        attac_player_key, defend_player_key = command.init()
        attac = AttacPlayer(attac_player_key, command)
        defend = DefendPlayer(defend_player_key, command)
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
                player = AttacPlayer(player_key, command, log_level=logging.DEBUG)
            elif game_resp.static_game_info.role == 1:
                player = DefendPlayer(player_key, command, log_level=logging.DEBUG)
            else:
                raise RuntimeError(f"Unkone role {game_resp.static_game_info.role}")

            player.act(resp)
        else:
            logger.info(f"Game finished ({game_resp.game_stage})")


if __name__ == "__main__":
    main()
