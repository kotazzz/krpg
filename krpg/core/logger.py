import os
import sys
from datetime import datetime as dt


class Logger:
    def __init__(
        self,
        level=5,
        message="[{time}] {color}{tag} : {text}{c}",
        file_message="[{full}] {tag} : {text}",
        filename="log%d%m%Y.txt",
        time="%H:%M:%S",
        full_time="%d.%m.%Y %H:%M:%S",
        file=True,
    ):
        self.time = time
        self.full_time = full_time
        self.message = message
        self.file_message = file_message
        self.filename = filename
        self.file = file
        self.colors = {
            "red": "\033[91m",
            "yellow": "\033[93m",
            "red_bg": "\033[41m",
            "green": "\033[32m",
            "blue": "\033[34m",
        }
        self.critical = lambda msg: level > 0 and self.send(
            "CRITICAL", msg, "red_bg", True
        )
        self.error = lambda msg: level > 1 and self.send("ERROR", msg, "red", True)
        self.warning = lambda msg: level > 2 and self.send("WARNING", msg, "yellow")
        self.info = lambda msg: level > 3 and self.send("INFO", msg, "green")
        self.debug = lambda msg: level > 4 and self.send("DEBUG", msg, "blue")
        self.file_name = dt.now().strftime(self.filename)
        self.filesend(
            "Log file created at {time}\n".format(
                time=dt.now().strftime(self.full_time)
            )
        )

    def filesend(self, msg):
        if self.file:
            open(self.file_name, "wa"[os.path.exists(self.file_name)]).write(msg)

    def send(self, tag, text, color, err=False):
        ts = dt.now()
        time = ts.strftime(self.time)
        full = ts.strftime(self.full_time)
        formatmap = {
            "time": time,
            "full": full,
            "tag": tag,
            "text": text,
            "color": self.colors[color],
            "c": "\033[0m",
        }
        s = sys.stderr if err else sys.stdout
        s.write(self.message.format(**formatmap) + "\n")
        self.filesend(self.file_message.format(**formatmap) + "\n")
