import logging

import click

import click_log

from .api import ApiClient
from .modem import demod, mod
from .node import Ap, Integer
from .operators import Cons, Nil
from .game_state import GameResponse

import threading


class LogFormatter(logging.Formatter):
    colors = {
        "error": dict(fg="red"),
        "exception": dict(fg="red"),
        "critical": dict(fg="red"),
        "debug": dict(fg="blue"),
        "warning": dict(fg="yellow"),
        "info": dict(fg="white"),
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

    def _send(self, request):
        modulated = mod(request)
        logger.debug(f"=> {request} ~~~~~> (send)")

        response = self.client.aliens_send(modulated)
        demodulated = demod(response)

        logger.debug(f"<= {demodulated} <~~~~~ (recv)")

        return demodulated

    def init(self):
        status, result = self._send((1, (0, ())))
        if status != 1:
            raise RuntimeError("Init Failed")

        (((_, (attac_player, ())), ((_, (def_player, ())), ())), ()) = result
        return attac_player, def_player

    def join(self, player_key):
        # (2, playerKey, (...unknown list...))
        req = (2, (player_key, ((), ())))
        status, result = self._send(req)
        if status != 1:
            raise RuntimeError(f"Join Failed: {player_key}")
        return result

    def start(self, player_key, ship_params=(1, (2, (3, (4, ()))))):
        req = (3, (player_key, (ship_params, ())))
        status, result = self._send(req)
        if status != 1:
            raise RuntimeError(f"Start Failed: {ship_params}")
        return result

    def command(self, player_key, commands):
        # (4, playerKey, (... ship commands? ...))
        req = (4, (player_key, (commands, ())))
        status, result = self._send(req)
        if status != 1:
            raise RuntimeError(f"Command Failed: {commands}")
        return result


class Player(threading.Thread):
    def __init__(self, player_key, command):
        super().__init__()
        self._player_key = player_key
        self._command = command
        self.log = logger.getChild("PLAYER")

    def run(self):
        self.log.debug("Start")
        resp = self._command.join(self._player_key)
        self.act(resp)

    def act(self):
        pass

    def accellerate(self, ship_id, vector=(0, 0)):
        vec = ()
        vec = (vector[0], vec)
        vec = (vector[1], vec)
        command_id = 0
        command = ()
        command = (vec, command)
        command = (ship_id, command)
        command = (command_id, command)
        self._command.command(self._player_key, command)

    def detonate(self, ship_id):
        command_id = 1
        command = ()
        command = (ship_id, command)
        command = (command_id, command)
        self._command.command(self._player_key, command)


class AttacPlayer(Player):
    def __init__(self, player_key, command):
        super().__init__(player_key, command)
        self.log = logger.getChild("ATTAC")
        self.log.info(f"Player Key: {self._player_key}")
        self._ship_params = (1, (2, (3, (4, ()))))

    def act(self, resp):
        self.game_response = GameResponse(resp)
        self.log.info(f"Start as {self.game_response.static_game_info.role}")
        resp = self._command.start(self._player_key, self._ship_params)
        self.game_response = GameResponse(resp)
        return self.log.info(self.game_response)


class DefendPlayer(Player):
    def __init__(self, player_key, command):
        super().__init__(player_key, command)
        self.log = logger.getChild("DEFEND")
        self.log.info(f"Player Key: {self._player_key}")
        self._ship_params = (1, (2, (3, (4, ()))))

    def act(self, resp):
        self.game_response = GameResponse(resp)
        self.log.info(f"Start as {self.game_response.static_game_info.role}")
        resp = self._command.start(self._player_key, self._ship_params)
        self.game_response = GameResponse(resp)
        self.log.info(self.game_response)
        s_u_c = self.game_response.game_state.ships_and_commands.ships_and_commands
        for (ship, commands,) in s_u_c:
            if ship.role == 1:
                # self.log.info("ACCELERATE")
                # self.accellerate(ship[0].ship_id, (1, 1))
                self.detonate(ship.ship_id)
                self.game_response = GameResponse(resp)
                self.log.info(self.game_response)


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
                player = AttacPlayer(player_key, command)
            elif game_resp.static_game_info.role == 1:
                player = DefendPlayer(player_key, command)
            else:
                raise RuntimeError(f"Unkone role {game_resp.static_game_info.role}")

            player.act(resp)
        else:
            logger.info(f"Game finished ({game_resp.game_stage})")


if __name__ == "__main__":
    main()
