from typing import Any
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


DEFAULT_LEVEL = 0


class KrpgConsole:
    """
    A class representing a console for the KRPG game.

    Attributes:
        console (Console): The console object.
        session (PromptSession): The prompt session object.
        bar (str): The bar text.
        log (logging.Logger): The logger object.
        handler (RichHandler): The rich handler object.
        queue (list): The command queue.
        history (list): The command history.
        levels (dict): The dictionary of console levels.

    Methods:
        get_history(): Returns the command history.
        setlevel(level): Sets the log level.
        print(*args, **kwargs): Prints the given arguments.
        set_bar(text): Sets the bar text.
        prompt(text, data, allow_empty, raw, check): Prompts the user for input.
        checked(prompt, checker, data, allow_empty, raw): Prompts the user for input and checks the input.
        confirm(prompt, exit_cmd): Prompts the user for confirmation.
        print_list(variants, view, title, empty): Prints a list of variants.
        menu(prompt, variants, exit_cmd, view, display, title, empty): Displays a menu and prompts the user for selection.
    """
    def __init__(self):

        self.console = Console()
        self.session = PromptSession()
        self.bar = ""
        self.log: logging.Logger = None

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
        self.setlevel(0)

        self.queue = []
        self.history = []

        self.levels: dict[int, ANSI] = {
            1: rich("[bold red]> [/]"),
            2: rich("[bold yellow]>> [/]", console=self.console),
            3: rich("[bold green]>>> [/]", console=self.console),
            4: rich("[bold blue]>>>> [/]", console=self.console),
            5: rich("[bold magenta]>>>>> [/]", console=self.console),
        }

    def get_history(self) -> list[str | Any]:
        """
        Returns the command history.

        Returns:
            list[str | Any]: The command history.
        """
        return [repr(i) if " " in i or not i else i for i in self.history]

    def setlevel(self, level) -> None:
        """
        Sets the log level.

        Parameters:
            level (int): The log level.
        """
        self.handler.level = level

    def print(self, *args, **kwargs) -> None:
        return self.console.print(*args, **kwargs, highlight=False)

    def set_bar(self, text: str) -> None:
        """
        Sets the bar text.

        Parameters:
            text (str): The bar text.
        """
        self.bar = rich(text)
    def prompt(self, text, data: dict[str, str] = None, allow_empty: bool = False, raw: bool = False, check: bool = False) -> str:
        """
        Prompts the user for input and returns the user's response.

        Args:
            text (str): The prompt text to display to the user.
            data (dict[str, str], optional): A dictionary of possible completions for the input. 
                The keys represent the possible input values, and the values represent the corresponding descriptions.
                Defaults to None.
            allow_empty (bool, optional): Specifies whether an empty input is allowed. 
                If True, an empty input will be returned as an empty string. 
                If False, the user will be prompted again until a non-empty input is provided.
                Defaults to False.
            raw (bool, optional): Specifies whether to return the user's input as is, without any processing.
                If True, the input will be returned as a string.
                If False, the input will be split into individual words and processed accordingly.
                Defaults to False.
            check (bool, optional): Specifies whether to check if the user's input is a valid option from the provided data.
                If True, the input will be checked against the keys in the data dictionary.
                If False, the input will be accepted as is.
                Defaults to False.

        Returns:
            str: The user's input as a string.
        """
        text = rich(text, console=self.console) if not isinstance(text, int) else self.levels[text]
        kwargs = {"bottom_toolbar": self.bar}
        if data:
            kwargs["completer"] = WordCompleter(list(data.keys()), meta_dict={i: rich(j) for i, j in data.items()})
        else:
            kwargs["completer"] = WordCompleter([])
        if not self.queue:
            while True:
                user = self.session.prompt(text, **kwargs)
                if raw:
                    self.history.append(user)
                    return user
                if not user and allow_empty:
                    self.history.append("")
                    return ""
                elif user:
                    try:
                        split = shlex.split(user)
                    except:
                        continue
                    self.queue.extend(split)
                    self.history.extend(split)
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
        title: str = None,
        empty: str = "Ничего нет",
    ):
        view = view or str
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
        if not isinstance(variants, list):
            variants = list(variants)
        view = view or str
        data = {str(i): view(j) for i, j in enumerate(variants, 1)}
        if exit_cmd:
            data[exit_cmd] = "cancel"

        if display:
            t = self.print_list(variants, view, title, empty)
            if exit_cmd:
                self.print(f"{t}[red]{exit_cmd}[/]) [blue]Выход")
        while True:
            res = self.prompt(prompt, data)
            if res == exit_cmd:
                return None
            elif res.isnumeric() and 1 <= int(res) <= len(variants):
                return variants[int(res) - 1]
