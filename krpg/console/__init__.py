import logging
import shlex
from typing import Any, Callable, Literal, Optional

import questionary
from prompt_toolkit import ANSI
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.shortcuts import PromptSession
from rich.console import Console
from rich.logging import RichHandler


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

        self.levels: dict[int, str] = {
            1: "[bold red]> [/]",
            2: "[bold yellow]>> [/]",
            3: "[bold green]>>> [/]",
            4: "[bold blue]>>>> [/]",
            5: "[bold magenta]>>>>> [/]",
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
    def print_list(self, items: list[Any], display: Callable[[Any], str]=str, marked: bool = False):
        if marked:
            for item in items:
                self.print(f"[blue]•[/]. [cyan]{display(item)}[/]")
        else:
            for i, item in enumerate(items, 1):
                self.print(f"[blue]{i}[/]. [cyan]{display(item)}[/]")
    
    # TODO: _create completer, _parse text
    def raw_prompt(self,
        text: str | int | ANSI,
        completer: Optional[dict[str, str]] = None,) -> str:
        prompt_completer = None
        if completer:
            completer = {shlex.quote(k): v for k, v in completer.items()}
            prompt_completer = WordCompleter(
                list(completer.keys()),
                meta_dict={i: rich_to_pt_ansi(j, console=self.console) for i, j in completer.items()},
            )
        if isinstance(text, int):
            try:
                text = self.levels[text]
            except KeyError:
                raise ValueError(f"Unknown level: {text}")
        return self.session.prompt(text, completer=prompt_completer)
    
    def prompt[T: Any](
        self,
        text: str | int | ANSI,
        completer: Optional[dict[str, str]] = None,
        allow_empty: bool = False,
        check_completer: bool = False,
        validator: Callable[[str], bool] | None = None,
        transformer: Callable[[str], T] = lambda x: x, #  type: ignore
    ) -> T | None:
        prompt_completer = None
        if completer:
            completer = {shlex.quote(k): v for k, v in completer.items()}
            prompt_completer = WordCompleter(
                list(completer.keys()),
                meta_dict={i: rich_to_pt_ansi(j, console=self.console) for i, j in completer.items()},
            )

        if isinstance(text, int):
            try:
                text = self.levels[text]
            except KeyError:
                raise ValueError(f"Unknown level: {text}")
            
        if isinstance(text, str):
            text = rich_to_pt_ansi(text, console=self.console)

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

            if item == "e":
                return None
            if check(item):
                return transformer(item)
                

    def menu(self, title: str, options: dict[str, Any]) -> Any:
        choices = [questionary.Choice([("green", i)], value=j) for i, j in options.items()]
        s = questionary.Style(
            [
                ("question", "red bold"),
            ]
        )
        return questionary.select(title, choices, qmark="", instruction=" ", style=s).ask()

    def select[T: Any](self, title: str, options: dict[str, T], indexed: bool = False) -> T | None:
        if self.queue:
            if indexed:
                completer = {str(i): v for i, v in enumerate(options.keys(), 1)}
                res = self.prompt(title, completer, validator=lambda x: x.isdigit() and 0 < int(x) <= len(options), transformer=int)
                if not res:
                    return None
                return list(options.values())[res-1]
            else:
                completer = {i: str(j) for i, j in options.items()}
                res = self.prompt(title, completer, validator=lambda x: x in options)
                if not res:
                    return None
                return options[res]
        else:
            return self.menu(title, options)
    
    def list_select[T](self, title: str, options: list[T], display:Callable[[Any], str]=str, hide: bool = False) -> T | None:
        if not hide:
            self.print_list(options, display)
        res = self.prompt(title, {str(i): display(j) for i, j in enumerate(options, 1)}, check_completer=True)
        if res:
            return options[int(res)-1]
        return None

    def confirm(self, prompt: str, allow_exit: bool = True) -> bool | None:
        while True:
            res: bool | None = questionary.confirm(prompt).ask()
            if res or not allow_exit:
                return res

    def __repr__(self) -> Literal["<Console>"]:
        return "<Console>"
