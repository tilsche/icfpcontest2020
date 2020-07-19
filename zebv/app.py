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

logging.basicConfig(level=logging.DEBUG, handlers=[handler])
# logging.basicConfig(level=logging.DEBUG)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


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
        self.log = logging.getLogger("PLAYER")

    def run(self):
        self.log.debug("Start")
        resp = self._command.join(self._player_key)
        self.game_response = GameResponse(resp)
        self.act()

    def act(self):
        pass


class AttacPlayer(Player):
    def __init__(self, player_key, command):
        super().__init__(player_key, command)
        self.log = logging.getLogger("ATTAC")
        self.log.info(f"Player Key: {self._player_key}")
        self._ship_params = (1, (2, (3, (4, ()))))

    def act(self):
        self.log.info(f"Start as {self.game_response.static_game_info.role}")
        resp = self._command.start(self._player_key, self._ship_params)
        self.game_response = GameResponse(resp)
        logging.info(self.game_response)


class DefendPlayer(Player):
    def __init__(self, player_key, command):
        super().__init__(player_key, command)
        self.log = logging.getLogger("DEFEND")
        self.log.info(f"Player Key: {self._player_key}")
        self._ship_params = (1, (2, (3, (4, ()))))

    def act(self):
        self.log.info(f"Start as {self.game_response.static_game_info.role}")
        resp = self._command.start(self._player_key, self._ship_params)
        self.game_response = GameResponse(resp)
        logging.info(self.game_response)


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
        attac_player_key, defend_player_key = command.init()
        attac = AttacPlayer(attac_player_key, command)
        defend = DefendPlayer(defend_player_key, command)
        attac.start()
        defend.start()

    else:
        resp = command.join(player_key)
        game_resp = GameResponse(resp)
        player = None
        if game_resp.static_game_info.role == 0:
            player = AttacPlayer(player_key, command)
        elif game_resp.static_game_info.role == 1:
            player = DefendPlayer(player_key, command)
        else:
            raise RuntimeError(f"Unkone role {game_resp.static_game_info.role}")

        player.act()


if __name__ == "__main__":
    main()
