from __future__ import annotations

from typing import TYPE_CHECKING, List
from krpg.actions import action
from krpg.events import Events
from krpg.inventory import Item

if TYPE_CHECKING:
    from krpg.game import Game
    from krpg.quests import QuestState
    from krpg.world import Location

class Counter:
    def __init__(self, event: str, name: str):
        self.event: str = event
        self.name: str = name
        self.count: int = 0
    def add(self, amount: int = 1):
        self.count += amount
    def listener(self, *args, **kwargs):
        self.add()
    
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
        on_heal(self, amount: int): Event handler for heal events.
        on_damage(self, amount: int): Event handler for damage events.
        on_quest_end(self): Event handler for quest end events.
        __repr__(self) -> str: Returns a string representation of the StatsManager object.
    """


    def __init__(self, game: Game):
        self.game = game
        self.counters: list[Counter] = [
             Counter(Events.COMMAND, "Исполнено команд"),
             Counter(Events.PICKUP, "Поднято предметов"),
             Counter(Events.ADD_MONEY, "Получено денег"),
             Counter(Events.REMOVE_MONEY, "Потрачено денег"),
             Counter(Events.MOVE, "Перемещений"),
             Counter(Events.SAVE, "Сохранений"),
             Counter(Events.KILL, "Убийств"),
             Counter(Events.HEAL, "Исцелений"),
             Counter(Events.DAMAGE, "Получено урона"),
             Counter(Events.QUEST_END, "Завершено квестов"),
        ]
        game.add_saver("stats", self.save, self.load)
        game.add_actions(self)
        
        for item in self.counters:
            game.events.listen(item.event, item.listener)
            game.log.debug(
                f"  [yellow3]Added stats [red]listener[/] for {item.event}", stacklevel=2
            )

    def save(self) -> List[int]:
        """
        Saves the counter values.

        Returns:
            List[int]: The counter values.
        """
        return [i.count for i in self.counters]

    def load(self, data: List[int]):
        """
        Loads the counter values.

        Args:
            data (List[int]): The counter values.
        """
        for i in self.counters:
            i.count = data.pop(0)
    
    @staticmethod
    @action("stats", "Посмотреть статистику", "Информация")
    def stats_action(game: Game):
        """
        Displays the statistics.

        Args:
            game (Game): The game instance.
        """
        game.console.print_list(
            # [f"[green]{i[0]}[/]: {i[1]}" for i in game.stats.counters.values()]
            [f"[green]{i.name}[/]: {i.count}" for i in game.stats.counters]
        )
