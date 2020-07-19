from logging import Formatter, LogRecord, getLogger

import click
import click_log


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


def get_logger(name: str):
    logger = getLogger(name)
    handler = click_log.ClickHandler()
    handler.formatter = LogFormatter()
    logger.addHandler(handler)
    return logger
