from __future__ import annotations
import attr
from attr import field


from typing import TYPE_CHECKING

from krpg.entity.utils import DEFAULT_DESCRIPTION, Nameable, _get_by_id

if TYPE_CHECKING:
    from krpg.entity.inventory import Item, Slot
    from krpg.entity.enums import ItemTag, TargetType
    from krpg.entity.effects import Effect


@attr.s(auto_attribs=True)
class SkillTree:
    learned: list[SkillState] = field(factory=list)
    skills: list[Skill] = field(factory=list)
    points: int = 0
    xp: int = 0
    _last_level: int = 0

    def add_xp(self, xp):
        self.xp += xp

    @property
    def required_xp(self):
        if self._last_level < 16:
            req = self._last_level**1.5 + self._last_level * 2 + 7
        if self._last_level < 31:
            req = self._last_level**1.3 + self._last_level * 4
        req = self._last_level**1.2 + self._last_level * 7
        return int(req)

    @property
    def level(self):
        while self.required_xp <= self.xp:
            self.xp -= self.required_xp
            self._last_level += 1
            self.points += 1

        return self._last_level

    def learn(self, item: str | Nameable):
        skill: Skill = _get_by_id(self.skills, item)
        if not skill:
            raise ValueError(f"No skill: {item}")
        self.learned.append(skill.new_instance)
        return self


@attr.s(auto_attribs=True)
class Skill(Nameable):
    cooldown: int
    prepare_time: int
    target: TargetType

    level: int = 1
    difficulty: int = 1

    cost_mp: int = 0
    cost_item: Item | ItemTag = None

    parrent: Skill = field(default=None, repr=False)
    childrens: list[Skill] = field(factory=list, repr=False)

    effects: list[Effect] = field(factory=list)
    description: str = DEFAULT_DESCRIPTION

    def link_children(self, skill: Skill):
        skill.parrent = self
        self.childrens.append(skill)

    @property
    def new_instance(self):
        return SkillState(self)


@attr.s(auto_attribs=True)
class SkillState:
    skill: Skill = field(repr=lambda x: repr(x.id))
    cooldown: int = 0
    use_slot: Slot = None
    prepare: int = 0

    @property
    def available(self):
        return self.cooldown == 0
