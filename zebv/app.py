from logging import INFO, Formatter, LogRecord, getLogger

import click
import click_log

from .api import ApiClient
from .modem import demod, mod
from .node import Ap, Number
from .operators import Cons, Nil


class LogFormatter(Formatter):
    colors = {
        "error": dict(fg="red"),
        "exception": dict(fg="red"),
        "critical": dict(fg="red"),
        "debug": dict(fg="blue"),
        "warning": dict(fg="yellow"),
    }

    def format(self, record: LogRecord):
        if not record.exc_info:
            level = record.levelname.lower()
            msg = record.getMessage()
            if level in self.colors:
                name_suffix = f"{record.name}:" if record.name != "root" else ""
                prefix = click.style(f"{level}:{name_suffix} ", **self.colors[level])
                msg = "\n".join(prefix + x for x in msg.splitlines())
            return msg
        return Formatter.format(self, record)


logger = getLogger(__name__)
handler = click_log.ClickHandler()
handler.formatter = LogFormatter()
logger.addHandler(handler)
logger.setLevel(INFO)


class Command:
    def __init__(self, player_key, client):
        self.player_key = int(player_key)
        self.client = client

    def _send(self, request):
        modulated = mod(request)
        logger.info(f"=> {request} -> (modulate) {modulated} ~~~~~> (send)")

        response = self.client.aliens_send(modulated)
        demodulated = demod(response)

        logger.info(f"<= {demodulated} <- (demodulate) {response} <~~~~~ (recv)")

        return demodulated

    def init(self):
        return self._send((0, ()))

    def join(self):
        return self._send((2, (self.player_key, ())))

    def start(self):
        return self._send((3, (self.player_key, ())))


@click.command()
@click.argument("server_url")
@click.argument("player_key")
@click.option("-k", "--api-key", default=None)
@click_log.simple_verbosity_option(logger)
def main(server_url, player_key, api_key):
    logger.info("ServerUrl: %s; PlayerKey: %s" % (server_url, player_key))

    client = ApiClient(server_url, api_key)
    # request = Ap(Ap(Cons(), Number(2)), Ap(Ap(Cons(), Number(int(player_key))), Nil()))

    command = Command(player_key, client)

    command.init()
    command.join()


if __name__ == "__main__":
    main()
