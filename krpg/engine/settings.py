from __future__ import annotations

from typing import TYPE_CHECKING, Any, Optional

from rich.table import Table

from krpg.actions import action
from krpg.data.themes import THEMES

if TYPE_CHECKING:
    from krpg.game import Game


class Param:
    def __init__(
        self,
        identifier: str,
        name: str,
        description: str,
        variants: Optional[dict[str, str]] = None,
    ):
        self.id: str = identifier
        self.name: str = name
        self.description: str = description
        self.variants: dict[str, str] = variants or {}
        self.value: Optional[str] = None

    def on_change(self, cb_param: Param, game: Game, new_value: str):
        """
        Changes the parameter value.

        Args:
            cb_param (Param): The parameter instance.
            game (Game): The game instance.
            new_value: The new value for the parameter.
        """
        raise NotImplementedError

    def __call__(self, *args, **kwargs):
        self.on_change(self, *args, **kwargs)

    def __repr__(self) -> str:
        return f"<Param {self.name!r}={self.value!r}>"


class ComplexParam:
    def __init__(self, identifier: str, name: str, description: str):
        self.id = identifier
        self.name = name
        self.description = description
        self.value: Any = None

    def callback(self, cb_param: ComplexParam, game: Game):
        """Callback func"""
        raise NotImplementedError

    def save(self, _: Game):
        """Save func"""
        return self.value

    def load(self, data: Any, _: Game):
        """Load func"""
        self.value = data


# TODO: Улучшить менеджер тем
class ThemeManager(ComplexParam):  # TODO: replace ComplexParam with Param?
    def __init__(self):
        super().__init__("theme", "Тема", "Изменяет тему консоли")

    def load(self, data: str, game: Game):
        self.value = data
        if self.value:
            self.change_theme(game, self.value)

    def callback(self, cb_param: ComplexParam, game: Game):
        """Callback func

        Parameters
        ----------
        cb_param : ComplexParam
            The parameter instance.
        game : Game
            The game instance.
        """

        def parse(theme):
            as_list = theme.split()
            return ("".join([f"[#{i}]█" for i in as_list[:-1]]), as_list[-1])

        page_size = 30
        collumns = 3
        page = 0

        data = [parse(i) for i in THEMES]
        pages = [
            data[i : i + page_size] for i in range(0, len(data), page_size)  # noqa
        ]  # noqa

        while True:
            table = Table(title="Выберите тему")
            for i in range(collumns):
                table.add_column("Тема")
                table.add_column("Название")
            cells = []
            for theme in pages[page]:
                cells.extend([theme[0], theme[1]])
            for i in range(0, len(cells), collumns * 2):
                table.add_row(*cells[i : i + collumns * 2])  # noqa

            game.console.print(table)
            game.console.print("Страница " + str(page + 1) + " из " + str(len(pages)))
            game.console.print("[green]p[/]<<< [green]n[/]>>> | [green]e[/] Выход")
            commands = {
                "n": "Следующая страница",
                "p": "Предыдущая страница",
                "e": "Выход",
            }
            commands |= {name: colors for colors, name in data}
            command = game.console.prompt(
                "[blue]Введите название темы или команду: [/]", commands
            )
            if command == "e":
                return
            if command == "n":
                page += 1
                if page >= len(pages):
                    page = 0
            elif command == "p":
                page -= 1
                if page < 0:
                    page = len(pages) - 1
            elif command in commands:
                self.change_theme(game, command)
                self.value = command
                game.show_logo()
                game.console.print("Тема успешно изменена")

    def change_theme(self, game: Game, name: str):
        """Changes the theme

        Parameters
        ----------
        game : Game
            The game instance.
        name : str
            The theme name.
        """
        colors = {i[-1]: [f"#{j}" for j in i[:-1]] for i in [i.split() for i in THEMES]}
        print(colors[name])
        game.console.set_theme(colors[name])


def param(
    identifier: str,
    name: str,
    description: str,
    variants: Optional[dict[str, str]] = None,
):
    """Decorator for creating a parameter.

    Parameters
    ----------
    identifier : str
        id of the parameter
    name : str
        name of the parameter
    description : str
        description of the parameter
    variants : Optional[dict[str, str]], optional
        variants of the parameter, by default None
    """

    def decorator(f):
        cb_param = Param(identifier, name, description, variants)
        cb_param.on_change = f
        return cb_param

    return decorator


class Settings:
    """
    Represents the settings of the game.

    Args:
        game (Game): The game instance.

    Attributes:
        params (list[Param]): The list of parameters.
        game (Game): The game instance.

    Methods:
        save: Saves the settings.
        load: Loads the settings.
        change_debug: Changes the debug setting.
        change_dummy: Changes the dummy setting.
        settings_command: Executes the settings command.
    """

    def __init__(self, game: Game):
        self.params: list[Param | ComplexParam] = []
        self.game = game
        self.game.add_actions(self)
        self.game.add_saver("settings", self.save, self.load)
        for attr in dir(self):
            val = getattr(self, attr)
            if isinstance(val, Param):
                self.params.append(val)
        self.params.append(ThemeManager())

    def save(self):
        """
        Saves the settings.

        Returns:
            dict: The saved settings.
        """
        return {i.id: i.value for i in self.params if i.value is not None}

    def load(self, data: dict):
        """
        Loads the settings.

        Args:
            data (dict): The settings data to load.
        """
        for cb_param in self.params:
            if isinstance(cb_param, ComplexParam):
                cb_param.load(data[cb_param.id], self.game)
            else:
                cb_param.value = data.pop(cb_param.id, None)

    @param(
        "debug",
        "Отладка",
        "Включает или отключает вывод отладки",
        {"enable": "Включить", "disable": "Выключить"},
    )
    @staticmethod
    def change_debug(cb_param: Param, game: Game, new_value):
        """
        Changes the debug setting.

        Args:
            param (Param): The parameter instance.
            game (Game): The game instance.
            new_value: The new value for the debug setting.
        """
        cb_param.value = new_value == "enable"
        game.set_debug(new_value == "enable")

        # game.console.set_theme(colors)

    @action("settings", "Настройки игры", "Игра")
    @staticmethod
    def settings_command(game: Game):
        """
        Executes the settings command.

        Args:
            game (Game): The game instance.
        """
        variants = game.settings.params

        def view(x):
            if isinstance(x, Param) | isinstance(x, ComplexParam):
                return f"[green]{x.name}[/] [yellow]\\[{x.value if x.value is not None else 'По умолчанию'}][/] - {x.description}"
            return "-"

        while True:
            cb_param: Param | ComplexParam = game.console.menu(
                2, variants, "e", view, title="Выберете параметр для изменения"
            )

            if not cb_param:
                return

            if isinstance(cb_param, ComplexParam):
                cb_param.callback(cb_param, game)

            else:
                if cb_param.variants:
                    new_value = game.console.menu(
                        3, list(cb_param.variants.items()), "e", lambda x: x[1]
                    )
                    if not new_value:
                        continue
                    new_value = new_value[0]
                else:
                    new_value = game.console.prompt(3)
                    if new_value == "e":
                        continue
                cb_param(game, new_value)

    def __repr__(self) -> str:
        return f"<Settings params={len(self.params)}>"
