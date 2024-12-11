from __future__ import annotations
import colorsys
import hashlib
from typing import Any, Generator

import attr

from krpg.actions import Action
from krpg.commands import command
from krpg.events_middleware import GameEvent
from krpg.utils import Nameable

@attr.s(auto_attribs=True)
class IntroduceNpc(GameEvent):
    npc: Npc

@attr.s(auto_attribs=True)
class TalkNpc(GameEvent):
    npc: Npc

@command
def introduce(npc: Npc) -> Generator[IntroduceNpc, Any, None]:
    yield IntroduceNpc(npc)
    npc.known = True

@attr.s(auto_attribs=True)
class Npc(Nameable):
    known: bool = False
    stage: int = 0
    stages: list[list[Action]] = attr.ib(factory=list)

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