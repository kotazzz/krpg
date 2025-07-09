from __future__ import annotations
from typing import TYPE_CHECKING, Any
import attr
from krpg.actions import Action, ActionCategory, ActionManager, action
from krpg.components import component
from krpg.engine.quests import EndQuest
from krpg.entity.inventory import PickupEvent
from krpg.events import listener
from krpg.events_middleware import GameEvent
from krpg.saves import Serializable

if TYPE_CHECKING:
    from krpg.game import Game


@attr.s(auto_attribs=True)
class ActionExecuted(GameEvent):
    action: Action


@component
class StatsActions(ActionManager):
    @action("stats", "Показать статистику", ActionCategory.INFO)
    @staticmethod
    def action_stats(game: Game) -> None:
        game.console.print("[green]Статистика:[/]")
        game.console.print(f"Команд выполнено: [yellow]{game.stats.commands_ran}[/]")
        game.console.print(f"Квестов завершено: [yellow]{game.stats.quests_completed}[/]")
        game.console.print(f"Предметов найдено: [yellow]{game.stats.items_found}[/]")


@component
@listener(ActionExecuted)
@staticmethod
def on_action_executed(event: ActionExecuted) -> None:
    game = event.game
    game.stats.commands_ran += 1


@component
@listener(EndQuest)
@staticmethod
def on_end_quest(event: EndQuest) -> None:
    game = event.game
    game.stats.quests_completed += 1


@component
@listener(PickupEvent)
@staticmethod
def on_item_found(event: PickupEvent) -> None:
    game = event.game
    game.stats.items_found += event.count


@attr.s(auto_attribs=True)
class Stats(Serializable):
    commands_ran: int = 0
    quests_completed: int = 0
    items_found: int = 0

    def serialize(self) -> Any:
        return [self.commands_ran, self.quests_completed, self.items_found]

    @classmethod
    def deserialize(cls, data: Any, *args: Any, **kwargs: Any) -> Stats:
        instance = cls.__new__(cls)
        instance.commands_ran = data[0]
        instance.quests_completed = data[1]
        instance.items_found = data[2]
        return instance
