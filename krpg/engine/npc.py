from __future__ import annotations
import colorsys
import hashlib
from typing import TYPE_CHECKING, Any, Generator

import attr

from krpg.actions import Action, ActionCategory, ActionManager, action
from krpg.commands import command
from krpg.components import component
from krpg.engine.executer import Scenario
from krpg.events_middleware import GameEvent
from krpg.utils import Nameable

if TYPE_CHECKING:
    from krpg.game import Game

@attr.s(auto_attribs=True)
class IntroduceNpc(GameEvent):
    npc: Npc

@attr.s(auto_attribs=True)
class TalkNpc(GameEvent):
    npc: Npc
    action: Action

@command
def introduce(npc: Npc) -> Generator[IntroduceNpc, Any, None]:
    yield IntroduceNpc(npc)
    npc.known = True

@command
def talk(game: Game, npc: Npc, action: Action):
    yield TalkNpc(npc, action)
    action.callback(game)

@component
class TalkAction(ActionManager):
    @action("talk", "Поговорить", ActionCategory.GAME)
    @staticmethod
    def action_talk(game: Game):
        npcs = game.world.current_location.npcs
        if not npcs:
            game.console.print("[red]Нет собеседника")
        npc = game.console.select("Выберите собеседника: ", {n.name: n for n in npcs}, True)
        if not npc:
            return
        action = game.console.select("Выберите тему: ", {a.name: a for a in npc.actions}, True)
        if action:
            action.script.run()
        


@attr.s(auto_attribs=True)
class Npc(Nameable):
    known: bool = False
    stage: int = 0
    stages: list[list[Scenario]] = attr.ib(factory=list)

    @property
    def actions(self) -> list[Scenario]:
        return self.stages[self.stage]
    
    @property
    def color(self) -> str:
        hash_hex = hashlib.md5(self.id.encode()).hexdigest()
        r, g, b = int(hash_hex[:2], 16), int(hash_hex[2:4], 16), int(hash_hex[4:6], 16)
        h, l, s = colorsys.rgb_to_hls(r / 255, g / 255, b / 255)  # noqa: E741
        nr, ng, nb = colorsys.hls_to_rgb(h, min(1, l * 1.1), min(1, s * 1.1))
        return f"#{int(nr * 255):02x}{int(ng * 255):02x}{int(nb * 255):02x}"

    @property
    def display(self) -> str:
        return f"[{self.color}]{self.name}" if self.known else "[gray]???"