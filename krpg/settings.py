from __future__ import annotations
from typing import TYPE_CHECKING, Any

from krpg.actions import action
from krpg.events import Events

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


def param(id: str, name: str, description: str, variants: dict[str, str] = None):
    def decorator(f):
        param = Param(id, name, description, variants)
        param.on_change = f
        return param

    return decorator


class Settings:
    def __init__(self, game: Game):
        self.params: list[Param] = []
        self.game = game
        self.game.add_actions(self)
        self.game.add_saver("settings", self.save, self.load)
        for attr in dir(self):
            val = getattr(self, attr)
            if isinstance(val, Param):
                self.params.append(val)

    def save(self):
        return {i.id: i.value for i in self.params if i.value is not None}

    def load(self, data: dict):
        for param in self.params:
            param.value = data.pop(param.id, None)

    @param(
        "debug",
        "Отладка",
        "Включает или отключает вывод отладки",
        {"enable": "Включить", "disable": "Выключить"},
    )
    def change_debug(param: Param, game: Game, new_value):
        game.debug = param.value = new_value == "enable"
        game.set_debug()

    @param("dummy", "Просто настройка", "Ничего не делает")
    def change_dummy(param: Param, game: Game, new_value):
        game.log.debug(f"New dummy value: {new_value} | {param=}, {game=}")

    @action("settings", "Настройки игры", "Игра")
    def settings_command(game: Game):
        variants = game.settings.params
        view = (
            lambda x: f"[green]{x.name}[/] [yellow]\[{x.value if x.value is not None else 'По умолчанию'}][/] - {x.description}"
            if isinstance(x, Param)
            else "-"
        )
        while True:
            param: Param = game.console.menu(
                2, variants, "e", view, title="Выберете параметр для изменения"
            )
            if not param:
                return
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
            game.events.dispatch(
                Events.SETTING_CHANGE, setting=param.id, value=new_value
            )
            param(game, new_value)

    def __repr__(self) -> str:
        return f"<Settings params={len(self.params)}>"