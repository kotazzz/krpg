from prompt_toolkit.completion import WordCompleter
from rich.console import Console
from prompt_toolkit import ANSI
import logging
from rich.logging import RichHandler
import shlex
from prompt_toolkit.shortcuts import PromptSession


def rich(*args, console=None, **kwargs):
    kwargs["end"] = kwargs.get("end", "")
    console = console or Console(markup=True)
    console = Console()
    with console.capture() as c:
        console.print(*args, **kwargs)
    return ANSI(c.get())


class KrpgConsole:
    def __init__(self):
        logging.basicConfig(
            level="DEBUG",
            format="%(message)s",
            datefmt="[%X]",
            handlers=[RichHandler()],
        )
        self.log = logging.getLogger("console")

        self.console = Console()
        self.session = PromptSession()
        self.queue = []

        self.levels = {
            1: rich("[bold red]> [/]"),
            2: rich("[bold yellow]>> [/]", console=self.console),
            3: rich("[bold green]>>> [/]", console=self.console),
            4: rich("[bold blue]>>>> [/]", console=self.console),
            5: rich("[bold magenta]>>>>> [/]", console=self.console),
        }

    def print(self, *args, **kwargs):
        return self.console.print(*args, **kwargs, highlight=False)

    def prompt(self, text, data=None, allow_empty=False):
        text = (
            rich(text, console=self.console)
            if not isinstance(text, int)
            else self.levels[text]
        )
        kwargs = {}
        if data:
            kwargs["completer"] = WordCompleter(
                list(data.keys()),
                meta_dict=data,
            )
        if not self.queue:
            while True:
                text = self.session.prompt(text, **kwargs)
                if not text and allow_empty:
                    return ""
                elif text:
                    self.queue.extend(shlex.split(text))
                    return self.queue.pop(0)
        else:
            cmd = self.queue.pop(0)
            cmdr = cmd.replace("[", "\[")
            self.console.print(f"[bold blue]\[AUTO][/] [blue]{cmdr}[/]")
            return cmd

    def confirm(self, prompt, exit_cmd=None):
        data = {"y": "yes", "n": "no"}
        if exit_cmd:
            data[exit_cmd] = "cancel"
        while True:
            res = self.prompt(prompt, data)
            if res == "y":
                return True
            elif res == "n":
                return False
            elif res == exit_cmd:
                return None
