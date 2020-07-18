from logging import INFO, Formatter, LogRecord, getLogger

import click

import click_log
from zebv.api import ApiClient
from zebv.modem import demod, mod


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


@click.command()
@click.argument("server_url")
@click.argument("player_key")
@click_log.simple_verbosity_option(logger)
def main(server_url, player_key):
    logger.info("ServerUrl: %s; PlayerKey: %s" % (server_url, player_key))
    return


if __name__ == "__main__":
    main()
