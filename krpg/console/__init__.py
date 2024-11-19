import logging
import shlex
from typing import Any, Callable, Literal, Optional

import questionary
from prompt_toolkit import ANSI
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.shortcuts import PromptSession
from rich.console import Console
from rich.logging import RichHandler

from krpg.utils import validate_select


def rich_to_pt_ansi(*args: str, console: Optional[Console] = None, **kwargs: Any) -> ANSI:
    kwargs["end"] = kwargs.get("end", "")
    console = console or Console(markup=True)
    console = Console()
    with console.capture() as c:
        console.print(*args, **kwargs)
    return ANSI(c.get())


DEFAULT_LEVEL = 1000


class KrpgConsole:
    def __init__(self) -> None:
        self.session: PromptSession[str] = PromptSession()

        self.console = Console()

        self.handler = RichHandler(
            level=DEFAULT_LEVEL,
            rich_tracebacks=True,
            tracebacks_show_locals=True,
            console=self.console,
            markup=True,
        )
        logging.basicConfig(
            level=DEFAULT_LEVEL,
            format="%(message)s",
            datefmt="[%X]",
            handlers=[self.handler],
        )
        self.log = logging.getLogger("console")

        self.queue: list[str] = []
        self.history: list[str] = []

        self.levels: dict[int, ANSI] = {
            1: rich_to_pt_ansi("[bold red]> [/]", console=self.console),
            2: rich_to_pt_ansi("[bold yellow]>> [/]", console=self.console),
            3: rich_to_pt_ansi("[bold green]>>> [/]", console=self.console),
            4: rich_to_pt_ansi("[bold blue]>>>> [/]", console=self.console),
            5: rich_to_pt_ansi("[bold magenta]>>>>> [/]", console=self.console),
        }

    def set_debug(self, debug: bool) -> None:
        level = logging.DEBUG if debug else DEFAULT_LEVEL
        self.handler.setLevel(level)
        self.log.setLevel(level)

    def get_history(self) -> list[str | Any]:
        return [repr(i) if " " in i or not i else i for i in self.history]

    def print(self, *args: Any, **kwargs: Any) -> None:
        """Prints the given arguments."""
        self.console.print(*args, **kwargs, highlight=False)

    def prompt(
        self,
        text: str | int | ANSI,
        completer: Optional[dict[str, str]] = None,
        allow_empty: bool = False,
        disable_parsing: bool = False,
        check_completer: bool = False,
        validator: Callable[[str], bool] | None = None,
    ) -> str:
        prompt_completer = None
        if completer:
            prompt_completer = WordCompleter(
                list(completer.keys()),
                meta_dict={i: rich_to_pt_ansi(j, console=self.console) for i, j in completer.items()},
            )

        if isinstance(text, int):
            try:
                text = self.levels[text]
            except KeyError:
                raise ValueError(f"Unknown level: {text}")

        def check(text: str) -> bool:
            if not text and not allow_empty:
                return False
            if completer and check_completer and text not in completer.keys():
                return False
            if validator and not validator(text):
                return False
            return True

        def parse(text: str) -> list[str]:
            try:
                items = shlex.split(text)
            except ValueError:
                return []
            self.history.extend(items)
            return items

        while True:
            if disable_parsing:
                res = self.session.prompt(text, completer=prompt_completer)
                return res
            if self.queue:
                item = self.queue.pop(0)
                escaped_item = item.replace("[", "\\[")
                self.print(f"[bold blue]\\[AUTO][/] [blue]{escaped_item}[/]")
            else:
                res = self.session.prompt(text, completer=prompt_completer)
                self.queue.extend(parse(res))
                if not self.queue:
                    continue
                item = self.queue.pop(0)

            if check(item):
                return item

    def menu(self, title: str, options: dict[str, Any]) -> Any:
        choices = [questionary.Choice([("green", i)], value=j) for i, j in options.items()]
        s = questionary.Style(
            [
                ("question", "red bold"),
            ]
        )
        return questionary.select(title, choices, qmark="", instruction=" ", style=s).ask()

    def select(self, title: str, options: dict[str, Any], use_console: bool = True) -> Any:
        # use_console = True = console.prompt + validator
        # else questionary.select

        if use_console:
            completer = {str(i): j for i, j in options.items()}
            res = self.prompt(title, completer=completer, validator=validate_select(1, len(options)))
            return options[res]
        else:
            return self.menu(title, options)

    def confirm(self, prompt: str, allow_exit: bool = True) -> bool | None:
        while True:
            res: bool | None = questionary.confirm(prompt).ask()
            if res or not allow_exit:
                return res

    def __repr__(self) -> Literal["<Console>"]:
        return "<Console>"
