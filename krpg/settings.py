from __future__ import annotations
from typing import TYPE_CHECKING

from krpg.actions import action
from krpg.events import Events
from krpg.data.themes import themes
from rich.table import Table

if TYPE_CHECKING:
    from krpg.game import Game


class Param:
    def __init__(
        self, id: str, name: str, description: str, variants: dict[str, str] = None
    ):
        self.id = id
        self.name = name
        self.description = description
        self.on_change = None
        self.variants = variants or {}
        self.value = None

    def __call__(self, *args, **kwargs):
        self.on_change(self, *args, **kwargs)

    def __repr__(self) -> str:
        return f"<Param {self.name!r}={self.value!r}>"


class ComplexParam:
    def __init__(self, id: str, name: str, description: str):
        self.id = id
        self.name = name
        self.description = description
        self.value = None

    def save(self, game: Game):
        return self.value

    def load(self, data: dict, game: Game):
        self.value = data


class ThemeManager(ComplexParam):
    def __init__(self):
        super().__init__("theme", "Тема", "Изменяет тему консоли")

    def load(self, data: dict, game: Game):
        self.value = data.pop(self.id, None)
        print(data)
        if self.value is not None:
            self.change_theme(game, self.value)

    def callback(self, param: ComplexParam, game: Game):
        """
        Changes the theme setting.

        Args:
            param (Param): The parameter instance.
            game (Game): The game instance.
        """

        def parse(theme):
            as_list = theme.split()
            return ("".join([f"[#{i}]█" for i in as_list[:-1]]), as_list[-1])

        page_size = 30
        collumns = 3
        page = 0

        data = [parse(i) for i in themes]
        pages = [data[i : i + page_size] for i in range(0, len(data), page_size)]

        while True:
            table = Table(title="Выберите тему")
            for i in range(collumns):
                table.add_column(f"Тема")
                table.add_column(f"Название")
            cells = []
            for theme in pages[page]:
                cells.extend([theme[0], theme[1]])
            for i in range(0, len(cells), collumns * 2):
                table.add_row(*cells[i : i + collumns * 2])

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
            elif command == "n":
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
        colors = {i[-1]: [f"#{j}" for j in i[:-1]] for i in [i.split() for i in themes]}
        print(colors[name])
        game.console.set_theme(colors[name])


def param(id: str, name: str, description: str, variants: dict[str, str] = None):
    def decorator(f):
        param = Param(id, name, description, variants)
        param.on_change = f
        return param

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
        self.params: list[Param] = []
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
        for param in self.params:
            if isinstance(param, ComplexParam):
                param.load(data, self.game)
            else:
                param.value = data.pop(param.id, None)

    @param(
        "debug",
        "Отладка",
        "Включает или отключает вывод отладки",
        {"enable": "Включить", "disable": "Выключить"},
    )
    def change_debug(param: Param, game: Game, new_value):
        """
        Changes the debug setting.

        Args:
            param (Param): The parameter instance.
            game (Game): The game instance.
            new_value: The new value for the debug setting.
        """
        param.value = new_value == "enable"
        game.set_debug(param.value)

        # game.console.set_theme(colors)

    @action("settings", "Настройки игры", "Игра")
    def settings_command(game: Game):
        """
        Executes the settings command.

        Args:
            game (Game): The game instance.
        """
        variants = game.settings.params
        view = (
            lambda x: f"[green]{x.name}[/] [yellow]\[{x.value if x.value is not None else 'По умолчанию'}][/] - {x.description}"
            if isinstance(x, Param) | isinstance(x, ComplexParam)
            else "-"
        )
        while True:
            param: Param | ComplexParam = game.console.menu(
                2, variants, "e", view, title="Выберете параметр для изменения"
            )

            if not param:
                return

            if isinstance(param, ComplexParam):
                param.callback(param, game)

            else:
                if param.variants:
                    new_value = game.console.menu(
                        3, list(param.variants.items()), "e", lambda x: x[1]
                    )
                    if not new_value:
                        continue
                    new_value = new_value[0]
                else:
                    new_value = game.console.prompt(3)
                    if new_value == "e":
                        continue
                param(game, new_value)

    def __repr__(self) -> str:
        return f"<Settings params={len(self.params)}>"
