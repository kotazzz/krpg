import io
from prompt_toolkit.data_structures import Size
from prompt_toolkit.output.windows10 import Windows10_Output
import sys
from rich.color import Color
from typing import Any, Callable, Optional, Sequence
from prompt_toolkit.completion import WordCompleter
from rich.console import Console
from prompt_toolkit import ANSI
import logging
from rich.logging import RichHandler
import shlex
from prompt_toolkit.shortcuts import PromptSession
from rich.color import ColorSystem
from rich.theme import Theme
from rich.theme import ThemeStackError
from rich.style import Style


def rich_to_pt_ansi(*args, console=None, **kwargs):
    kwargs["end"] = kwargs.get("end", "")
    console = console or Console(markup=True)
    console = Console()
    with console.capture() as c:
        console.print(*args, **kwargs)
    return ANSI(c.get())


DEFAULT_LEVEL = 0

class ConsoleHooked(Console):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._forced_reset = "\x1b[0m"
        
    def print(self, *args, **kwargs):
        # Получаем вывод, который должен попасть в консоль
        with self.capture() as capture:
            super().print(*args, **kwargs)
        # Добавляем "сброс" в начало
        text = '\x1b[0m'+capture.get()
        # Заменяем все сбросы на измененный стиль по умолчанию
        # _make_ansi_codes возвращает строку с кодами ANSI
        text = text.replace('\x1b[0m', "\x1b[0m"+self._forced_reset)
        text = text.replace('\n', '\x1b[K\n')
        # Записываем в stdout
        sys.stdout.write(text)


class WrappedStdout(io.TextIOBase):
    def __init__(self, forced_reset):
        self._forced_reset = forced_reset
        super().__init__()
    def write(self, text):
        text = text.replace('\x1b[0m', self._forced_reset)
        # text = text.replace('\n', '\x1b[K\n')
        # Записываем в stdout
        sys.stdout.write(text)
    def __call__(self, name) -> Any:
        # if it not __init__ or write - return from sys.stdout
        if name not in ('__init__', 'write'):
            return getattr(sys.stdout, name)
        

class PromptSessionHooked(PromptSession):
    pass
        
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

    def __init__(self) -> None:
        self.console = ConsoleHooked()
        
        self.session: PromptSession = PromptSession()
        self.bar = ""

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

        self.queue: list[str] = []
        self.history: list[str] = []

        self.levels: dict[int, ANSI] = {
            1: rich_to_pt_ansi("[bold red]> [/]", console=self.console),
            2: rich_to_pt_ansi("[bold yellow]>> [/]", console=self.console),
            3: rich_to_pt_ansi("[bold green]>>> [/]", console=self.console),
            4: rich_to_pt_ansi("[bold blue]>>>> [/]", console=self.console),
            5: rich_to_pt_ansi("[bold magenta]>>>>> [/]", console=self.console),
        }

    def reset_theme(self):
        try:
            self.console.pop_theme()
        except ThemeStackError:
            pass

    def set_theme(self, colors: list[str]):
        # Reset the theme to default
        self.reset_theme()
        
        # Get the default theme
        default = self.console._theme_stack._entries[0]

        # Map color names to corresponding ANSI codes
        color_names = [
            "black", "red", "green", "yellow", "blue", "magenta", "cyan", "white",
            "bright_black", "bright_red", "bright_green", "bright_yellow",
            "bright_blue", "bright_magenta", "bright_cyan", "bright_white"
        ]
        new_colors = dict(zip(color_names, colors))
        new_theme = default.copy()
        # Replace color values in the theme
        for name in color_names:
            new_theme[name] = Style.parse(new_colors[name])
            new_theme[f"on {name}"] = Style.parse(f"on {new_colors[name]}")
        
        for st in new_theme.values():
            if st.color and st.color.type == 1:
                
                # Перебираем все стили, по типу inspect.*, iso8601.*, repr.*, str.*
                # Если есть цвет и он является стандартным - подменяем на свой
                # С фоном по аналогии
                clr = new_colors[st.color.name]
                st._color = Color.parse(clr)
            if st.bgcolor is not None and st.bgcolor.type == 1:
                bg_clr = new_colors[st.bgcolor.name]
                st._bgcolor = Color.parse(bg_clr)

        new_theme['reset']._color = Color.parse(new_colors['white']) # TODO: Сделать отдельный цвет фона
        new_theme['reset']._bgcolor = Color.parse(new_colors['black'])
        new_theme['none']._color = Color.parse(new_colors['white'])
        new_theme['none']._bgcolor = Color.parse(new_colors['black'])
        
        # Apply the updated theme
        self.console.push_theme(Theme(new_theme))
        self.console._forced_reset = f"\x1b[{new_theme['none']._make_ansi_codes(ColorSystem.TRUECOLOR)}m"
        self.console.clear()
        
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
        self.bar = rich_to_pt_ansi(text, console=self.console)

    def prompt(
        self,
        text,
        data: Optional[dict[str, str]] = None,
        allow_empty: bool = False,
        raw: bool = False,
        check: bool = False,
    ) -> str:
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
        text = (
            rich_to_pt_ansi(text, console=self.console)
            if not isinstance(text, int)
            else self.levels[text]
        )
        kwargs: dict[str, Any] = {"bottom_toolbar": self.bar}
        data = data or {}
        if data:
            kwargs["completer"] = WordCompleter(
                list(data.keys()), meta_dict={i: rich_to_pt_ansi(j, console=self.console) for i, j in data.items()}
            )
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
            cmdr = cmd.replace("[", "\\[")
            self.console.print(f"[bold blue]\\[AUTO][/] [blue]{cmdr}[/]")
            return cmd

    def checked(
        self, prompt, checker: Callable[[str], bool], data: dict = {}, allow_empty: bool=False, raw: bool=False
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
        view: Optional[Callable[[str], str]] = None,
        title: Optional[str] = None,
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
        prompt: int | str,
        variants: Sequence,
        exit_cmd=None,
        view: Optional[Callable] = None,
        display: bool = True,
        title: Optional[str] = None,
        empty: str = "Ничего нет",
     ) -> Any:
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
