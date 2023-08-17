from __future__ import annotations

from typing import TYPE_CHECKING
from krpg.actions import action
from krpg.events import Events
from krpg.inventory import Item
from krpg.world import Location

if TYPE_CHECKING:
    from krpg.game import Game


class StatsManager:
    def __init__(self, game: Game):
        self.game = game

        self.counters = {
            "c": ["Исполнено команд", 0],
            "p": ["Поднято предметов", 0],
            "a": ["Получено денег", 0],
            "r": ["Потрачено денег", 0],
            "m": ["Перемещений", 0],
            "s": ["Сохранений", 0],
            "k": ["Убийств", 0],
        }
        game.add_saver("stats", self.save, self.load)
        game.add_actions(self)
        for attr in filter(lambda x: x.startswith("on_"), dir(self)):
            cb = getattr(self, attr)
            game.events.listen(attr[3:], cb)
            game.log.debug(f"Added stats [red]listener[/] for {attr[3:]}")

    def save(self):
        return [i[1] for i in self.counters.values()]

    def load(self, data):
        for i, c in enumerate(self.counters):
            self.counters[c][1] = data[i]

    @action("stats", "Посмотреть статистику", "Информация")
    def stats_action(game: Game):
        game.console.print_list(
            [f"[green]{i[0]}[/]: {i[1]}" for i in game.stats.counters.values()]
        )

    def on_command(self, command: str):
        self.counters["c"][1] += 1

    def on_pickup(self, item: Item, amount: int):
        self.counters["p"][1] += amount

    def on_add_money(self, amount: int, new_balance: int):
        self.counters["a"][1] += amount

    def on_remove_money(self, amount: int, new_balance: int):
        self.counters["r"][1] += amount

    def on_move(self, before: Location, after: Location):
        self.counters["m"][1] += 1

    def on_save(self):
        self.counters["s"][1] += 1

    def on_kill(self, monster_id):
        self.counters["k"][1] += 1

    def __repr__(self) -> str:
        return f"<StatsManger>"
