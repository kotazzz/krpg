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

        self.console = Console()
        self.session = PromptSession()

        logging.basicConfig(
            level="DEBUG",
            format="%(message)s",
            datefmt="[%X]",
            handlers=[
                RichHandler(
                    rich_tracebacks=True,
                    tracebacks_show_locals=True,
                    console=self.console,
                    markup=True,
                )
            ],
        )
        self.log = logging.getLogger("console")

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

    def prompt(
        self,
        text,
        data: dict[str, str] = None,
        allow_empty=False,
        raw=False,
        check: bool = False,
    ) -> str:
        text = (
            rich(text, console=self.console)
            if not isinstance(text, int)
            else self.levels[text]
        )
        kwargs = {}
        if data:
            kwargs["completer"] = WordCompleter(
                list(data.keys()),
                meta_dict={i: rich(j) for i, j in data.items()},
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
                    el = self.queue.pop(0)
                    if not check or el in data:
                        return el
        else:
            cmd = self.queue.pop(0)
            cmdr = cmd.replace("[", "\[")
            self.console.print(f"[bold blue]\[AUTO][/] [blue]{cmdr}[/]")
            return cmd

    def checked(
        self, prompt, checker: bool, data: dict = {}, allow_empty=False, raw=False
    ):
        while True:
            res = self.prompt(prompt, data, allow_empty, raw)
            if checker(res):
                return res

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

    def print_list(
        self,
        variants: list,
        view: callable = None,
        display: bool = True,
        title: str = None,
        empty: str = "Ничего нет",
    ):
        t = ""
        if title:
            t = "  "
            self.print(f"[b green]{title}")
        if not variants:
            self.print(f"{t}[b red]{empty}")
            return t
        for i, v in enumerate(variants, 1):
            self.print(f"{t}[green]{i}[/]) [blue]{view(v)}")
        return t

    def menu(
        self,
        prompt,
        variants: list,
        exit_cmd=None,
        view: callable = None,
        display: bool = True,
        title: str = None,
        empty: str = "Ничего нет",
    ):
        view = view or str
        data = {str(i): view(j) for i, j in enumerate(variants, 1)}
        if exit_cmd:
            data[exit_cmd] = "cancel"

        if display:
            t = self.print_list(variants, view, display, title, empty)
            if exit_cmd:
                self.print(f"{t}[red]{exit_cmd}[/]) [blue]Выход")
        while True:
            res = self.prompt(prompt, data)
            if res == exit_cmd:
                return None
            elif res.isnumeric() and 1 <= int(res) <= len(variants):
                return variants[int(res) - 1]
