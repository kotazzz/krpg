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

    def raw_prompt(self, text, data={}):
        kwargs = {}
        if data:
            kwargs["completer"] = WordCompleter(
                list(data.keys()),
                meta_dict=data,
            )
        text = (
            rich(text, console=self.console)
            if not isinstance(text, int)
            else self.levels[text]
        )
        return self.session.prompt(text, **kwargs)

    def prompt(self, *args, **kwargs):
        if not self.queue:
            text = self.raw_prompt(*args, **kwargs)
            self.queue.extend(shlex.split(text))
            return self.queue.pop(0)
        else:
            cmd = self.queue.pop(0)
            cmdr = cmd.replace("[", "\[")
            self.console.print(f"[bold blue]\[AUTO][/] [blue]{cmdr}[/]")
            return cmd
