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

    def prompt(self, text, data=None, allow_empty=False, raw=False) -> str:
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
                user = self.session.prompt(text, **kwargs)
                if raw:
                    return user
                if not user and allow_empty:
                    return ""
                elif user:
                    try:
                        split = shlex.split(user)
                    except:
                        continue
                    self.queue.extend(split)
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

    def __repr__(self):
        return "<Console>"

    def menu(self, prompt, variants: list, exit_cmd=None, view:callable=None, display:bool=True):
        view = view or str
        data = {str(i):view(j) for i, j in enumerate(variants, 1)}
        if exit_cmd:
            data[exit_cmd] = "cancel"
        if display:
            for i, v in enumerate(variants, 1):
                self.print(f'[green]{i}[/]) [blue]{view(v)}')
        while True:
            res = self.prompt(prompt, data)
            if res == exit_cmd:
                return None
            elif res.isnumeric() and 1 <= int(res) <= len(variants):
                return variants[int(res)-1]
            

