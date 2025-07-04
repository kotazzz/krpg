from __future__ import annotations

from typing import TYPE_CHECKING, Any, Self

import attr
from attr import field

from krpg.bestiary import BESTIARY
from krpg.entity.enums import TargetType
from krpg.saves import Savable
from krpg.utils import DEFAULT_DESCRIPTION, Nameable, get_by_id

if TYPE_CHECKING:
    from krpg.entity.effects import Effect
    from krpg.entity.enums import ItemTag
    from krpg.entity.inventory import Item, Slot


@attr.s(auto_attribs=True)
class Skill(Nameable):
    cooldown: int = 0
    prepare_time: int = 0
    target: TargetType = TargetType.ENTITY

    level: int = 1
    difficulty: int = 1

    cost_mp: int = 0
    cost_item: Item | ItemTag | None = None

    parent: Skill = field(default=None, repr=False)
    children: list[Skill] = field(factory=lambda: [], repr=False)

    effects: list[Effect] = field(factory=lambda: [], repr=False)
    description: str = DEFAULT_DESCRIPTION

    def link_children(self, skill: Skill) -> None:
        skill.parent = self
        self.children.append(skill)

    @property
    def new_instance(self) -> SkillState:
        return SkillState(self)


@attr.s(auto_attribs=True)
class SkillState(Savable):
    skill: Skill = field(repr=lambda x: repr(x.id))
    cooldown: int = 0
    use_slot: Slot | None = None
    prepare: int = 0

    def serialize(self) -> Any:
        return {
            "skill": self.skill.id,
            "cooldown": self.cooldown,
            # FIXME: use link to inventory
            "use_slot": self.use_slot.serialize() if self.use_slot else None,
            "prepare": self.prepare,
        }

    @classmethod
    def deserialize(cls, data: Any, *args: Any, **kwargs: Any) -> SkillState:
        instance = cls.__new__(cls)
        instance.skill = BESTIARY.strict_get_entity_by_id(data["skill"], Skill)
        instance.cooldown = data["cooldown"]
        instance.use_slot = BESTIARY.strict_get_entity_by_id(data["use_slot"], Slot) if data["use_slot"] else None
        instance.prepare = data["prepare"]
        return instance

    @property
    def available(self) -> bool:
        return self.cooldown == 0


@attr.s(auto_attribs=True)
class SkillTree(Savable):
    skills: list[Skill] = field(factory=list[Skill])
    learned: list[SkillState] = field(factory=list[SkillState])
    points: int = 0
    xp: int = 0
    _last_level: int = 0

    def serialize(self) -> Any:
        return {
            "skills": [skill.id for skill in self.skills],
            "learned": [state.serialize() for state in self.learned],
            "points": self.points,
            "xp": self.xp,
            "last_level": self._last_level,
        }

    @classmethod
    def deserialize(cls, data: Any, *args: Any, **kwargs: Any) -> SkillTree:
        instance = cls.__new__(cls)
        instance.skills = [BESTIARY.strict_get_entity_by_id(skill_data, Skill) for skill_data in data["skills"]]
        instance.learned = [SkillState.deserialize(state_data) for state_data in data["learned"]]
        instance.points = data["points"]
        instance.xp = data["xp"]
        instance._last_level = data["last_level"]
        return instance

    def add_xp(self, xp: int) -> None:
        self.xp += xp

    @property
    def required_xp(self) -> int:
        if self._last_level < 16:
            req = self._last_level**1.5 + self._last_level * 2 + 7
        if self._last_level < 31:
            req = self._last_level**1.3 + self._last_level * 4
        req = self._last_level**1.2 + self._last_level * 7
        return int(req)

    @property
    def level(self) -> int:
        while self.required_xp <= self.xp:
            self.xp -= self.required_xp
            self._last_level += 1
            self.points += 1

        return self._last_level

    def learn(self, item: str | Nameable) -> Self:
        res = get_by_id(self.skills, item)
        if not res or not isinstance(res, Skill):
            raise Exception(f"Not found: {item}")
        skill: Skill = res
        if not skill:
            raise ValueError(f"No skill: {item}")
        self.learned.append(skill.new_instance)
        return self
