from __future__ import annotations

from typing import TYPE_CHECKING, List
from krpg.actions import action
from krpg.inventory import Item
from krpg.world import Location

if TYPE_CHECKING:
    from krpg.game import Game


class StatsManager:
    """
    A class that manages the statistics of a game.

    Attributes:
        game (Game): The game instance.
        counters (dict): A dictionary that stores the counters for different statistics.

    Methods:
        __init__(self, game: Game): Initializes the StatsManager object.
        save(self) -> List[int]: Saves the counter values.
        load(self, data: List[int]): Loads the counter values.
        stats_action(game: Game): Displays the statistics.
        on_command(self, command: str): Event handler for command events.
        on_pickup(self, item: Item, amount: int): Event handler for pickup events.
        on_add_money(self, amount: int, new_balance: int): Event handler for add money events.
        on_remove_money(self, amount: int, new_balance: int): Event handler for remove money events.
        on_move(self, before: Location, after: Location): Event handler for move events.
        on_save(self): Event handler for save events.
        on_kill(self, monster_id): Event handler for kill events.
        __repr__(self) -> str: Returns a string representation of the StatsManager object.
    """

    def __init__(self, game: Game):
        self.game = game
        # TODO: Добавить счетчик квестов
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
            game.log.debug(
                f"  [yellow3]Added stats [red]listener[/] for {attr[3:]}", stacklevel=2
            )

    def save(self) -> List[int]:
        """
        Saves the counter values.

        Returns:
            List[int]: The counter values.
        """
        return [i[1] for i in self.counters.values()]

    def load(self, data: List[int]):
        """
        Loads the counter values.

        Args:
            data (List[int]): The counter values.
        """
        for i, c in enumerate(self.counters):
            self.counters[c][1] = data[i]

    @action("stats", "Посмотреть статистику", "Информация")
    def stats_action(game: Game):
        """
        Displays the statistics.

        Args:
            game (Game): The game instance.
        """
        game.console.print_list(
            [f"[green]{i[0]}[/]: {i[1]}" for i in game.stats.counters.values()]
        )

    def on_command(self, command: str):
        """
        Event handler for command events.

        Args:
            command (str): The command.
        """
        self.counters["c"][1] += 1

    def on_pickup(self, item: Item, amount: int, total: int):
        """
        Event handler for pickup events.

        Args:
            item (Item): The picked up item.
            amount (int): The amount of items picked up.
        """
        self.counters["p"][1] += amount

    def on_add_money(self, amount: int, new_balance: int):
        """
        Event handler for add money events.

        Args:
            amount (int): The amount of money added.
            new_balance (int): The new balance after adding money.
        """
        self.counters["a"][1] += amount

    def on_remove_money(self, amount: int, new_balance: int):
        """
        Event handler for remove money events.

        Args:
            amount (int): The amount of money removed.
            new_balance (int): The new balance after removing money.
        """
        self.counters["r"][1] += amount

    def on_move(self, before: Location, after: Location):
        """
        Event handler for move events.

        Args:
            before (Location): The location before moving.
            after (Location): The location after moving.
        """
        self.counters["m"][1] += 1

    def on_save(self):
        """
        Event handler for save events.
        """
        self.counters["s"][1] += 1

    def on_kill(self, monster_id):
        """
        Event handler for kill events.

        Args:
            monster_id: The ID of the killed monster.
        """
        self.counters["k"][1] += 1

    def __repr__(self) -> str:
        """
        Returns a string representation of the StatsManager object.

        Returns:
            str: The string representation of the StatsManager object.
        """
        return "<StatsManger>"
