from __future__ import annotations
import colorsys
import hashlib
from typing import TYPE_CHECKING, Any, Generator

import attr

from krpg.actions import Action, ActionCategory, ActionManager, action
from krpg.bestiary import BESTIARY
from krpg.commands import command
from krpg.components import component
from krpg.events_middleware import GameEvent
from krpg.saves import Savable
from krpg.utils import Nameable

if TYPE_CHECKING:
    from krpg.game import Game
    from krpg.engine.executer import NamedScript


@attr.s(auto_attribs=True)
class IntroduceNpc(GameEvent):
    npc: NpcState


@attr.s(auto_attribs=True)
class TalkNpc(GameEvent):
    npc: NpcState
    action: Action


@command
def introduce(npc: NpcState) -> Generator[IntroduceNpc, Any, None]:
    yield IntroduceNpc(npc)
    npc.known = True


@command
def talk(npc: NpcState, action: Action) -> Generator[TalkNpc, Any, None]:
    yield TalkNpc(npc, action)


@component
class TalkAction(ActionManager):
    @action("talk", "Поговорить", ActionCategory.GAME)
    @staticmethod
    def action_talk(game: Game) -> None:
        npc_list = game.world.current_location.npcs
        npcs = game.npc_manager.get_states(npc_list)
        if not npcs:
            game.console.print("[red]Нет собеседника")
            return
        npc = game.console.select("Выберите собеседника: ", {n.npc.name: n for n in npcs}, True)
        if not npc:
            return
        action = game.execute_action(npc.actions, "Выберите тему", interactive=True)
        if action:
            game.commands.execute(talk(npc, action))


@attr.s(auto_attribs=True)
class NpcState(Savable):
    npc: Npc
    known: bool = False
    stage: int = 0

    def serialize(self) -> Any:
        return {"npc": self.npc.id, "known": self.known, "stage": self.stage}

    @classmethod
    def deserialize(cls, data: Any, *args: Any, **kwargs: Any) -> NpcState:
        npc = BESTIARY.strict_get_entity_by_id(data["npc"], Npc)
        if not npc:
            raise ValueError(f"Unknown NPC ID: {data['npc']}")
        return cls(npc=npc, known=data["known"], stage=data["stage"])

    @property
    def actions(self) -> list[Action]:
        return [a.as_action for a in self.npc.stages[self.stage]]

    @property
    def display(self) -> str:
        return f"[{self.npc.color}]{self.npc.name}[{self.npc.color2}]" if self.known else "[gray]???[/]"

    @classmethod
    def from_npc(cls, npc: Npc) -> NpcState:
        return cls(npc=npc)


@attr.s(auto_attribs=True)
class Npc(Nameable):
    stages: list[list[NamedScript]] = attr.ib(factory=lambda: [], repr=False)

    color: str = attr.ib(init=False, repr=False)
    color2: str = attr.ib(init=False, repr=False)

    def __attrs_post_init__(self):
        hash_hex = hashlib.md5(self.id.encode()).hexdigest()
        r, g, b = int(hash_hex[:2], 16), int(hash_hex[2:4], 16), int(hash_hex[4:6], 16)
        h, l, s = colorsys.rgb_to_hls(r / 255, g / 255, b / 255)  # noqa: E741
        nr, ng, nb = colorsys.hls_to_rgb(h, min(1, l * 1.1), min(1, s * 1.1))
        tr, tg, tb = colorsys.hls_to_rgb(h, 0.7, 0.7)
        clr1, clr2 = (f"#{int(nr * 255):02x}{int(ng * 255):02x}{int(nb * 255):02x}", f"#{int(tr * 255):02x}{int(tg * 255):02x}{int(tb * 255):02x}")

        self.color = clr1
        self.color2 = clr2


@attr.s(auto_attribs=True)
class NpcManager(Savable):
    npcs: dict[str, NpcState] = attr.ib(factory=lambda: {})

    def serialize(self) -> Any:
        return [npc_state.serialize() for npc_state in self.npcs.values()]

    @classmethod
    def deserialize(cls, data: Any, *args: Any, **kwargs: Any) -> NpcManager:
        instance = cls()
        instance.npcs = {npc["npc"]: NpcState.deserialize(npc) for npc in data}
        return instance

    def __attrs_post_init__(self):
        all_npcs = BESTIARY.get_all(Npc)
        for npc in all_npcs:
            self.npcs[npc.id] = NpcState.from_npc(npc)

    def get_states(self, npcs: list[Npc]) -> list[NpcState]:
        states: list[NpcState] = []
        for npc in npcs:
            if npc.id in self.npcs:
                states.append(self.npcs[npc.id])
            else:
                raise ValueError(f"NPC {npc.id} not found")
        return states
