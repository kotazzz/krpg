from __future__ import annotations

from typing import TYPE_CHECKING, Any, Literal, Self

import attr
from attr import field

from krpg.entity.effects import EffectState, EntityModifier, ItemModifier
from krpg.entity.enums import Attribute, Body, EntityScales, ItemTag, TargetType
from krpg.entity.inventory import Inventory, Item
from krpg.entity.scale import Scale
from krpg.entity.skills import SkillState, SkillTree
from krpg.utils import Nameable

if TYPE_CHECKING:
    from krpg.entity.inventory import Item


@attr.s(auto_attribs=True)
class Entity(Nameable):
    skills: SkillTree = SkillTree()
    inventory: Inventory = field(factory=Inventory.basic)  # TODO: Field -> attrib
    effects: list[EffectState] = field(factory=lambda: [])
    _parts: dict[Body, Scale] = field(factory=lambda: {}, init=False)
    _scales: dict[EntityScales, Scale] = field(factory=lambda: {}, init=False)
    _attributes: dict[Attribute, Scale] = field(factory=lambda: {}, init=False)
    queue_actions: list[SkillState] = field(factory=lambda: [])

    def __attrs_post_init__(self) -> None:
        for _ in Body:
            if _ not in self.parts:
                name, desc = _.value
                self.parts[_] = Scale(name, desc, base_max_value=100)

        for _ in Attribute:
            if _ not in self.attributes:
                name, desc = _.value
                self.attributes[_] = Scale.infinite(name, desc)

        for _ in EntityScales:
            if _ not in self.scales:
                name, desc = _.value[:2]
                self.scales[_] = Scale(name, desc, base_max_value=100)

    def calc_bonus(self, attr: Attribute, max_value_bonus: bool = False) -> float:
        # сила - наносимый урон
        # выносливость - защита
        # интеллект - стоимость манны
        # ловкость - скорость подготовки действий
        # восприятие - шанс крита, шанс знать действия врага первым
        # харизма - влияет на НПС
        # мудрость - получаемый опыт
        attr_value = self.attributes[attr].value
        formulas: dict[str, dict[Attribute, float]] = {
            "mvb": {
                Attribute.STRENGTH: 0.01 * attr_value,
                Attribute.PERCEPTION: 0.01 * attr_value,
                Attribute.ENDURANCE: 0.02 * attr_value,
                Attribute.CHARISMA: 0.03 * attr_value,
                Attribute.AGILITY: 0.01 * attr_value,
                Attribute.INTELLIGENSE: 0.01 * attr_value,
                Attribute.WISDOM: 0.01 * attr_value,
            },
            "momentum": {
                Attribute.STRENGTH: 1 + 0.01 * attr_value,
                Attribute.PERCEPTION: 1 + 0.01 * attr_value,
                Attribute.ENDURANCE: 1 + 0.02 * attr_value,
                Attribute.CHARISMA: 1 + 0.03 * attr_value,
                Attribute.AGILITY: 1,
                Attribute.INTELLIGENSE: 1,
                Attribute.WISDOM: 1,
            },
        }
        if max_value_bonus:
            return formulas["mvb"][attr]
        return formulas["momentum"][attr]

    @property
    def actions(self) -> list[SkillState]:
        return self.inventory.actionable + self.skills.learned

    def set_attr(self, key: Attribute, value: int) -> Self:
        self.attributes[key].set(value)
        return self

    @property
    def modifiers(self) -> list[EntityModifier | ItemModifier]:
        modifiers: list[EntityModifier | ItemModifier] = []
        for effect in self.inventory.effects:
            if effect.effect.time == -1:
                modifiers.extend(effect.effect.modifiers)
        return modifiers

    @property
    def parts(self) -> dict[Body, Scale]:
        p = {i: 0.0 for i in self._parts}

        for mod in self.modifiers:
            if isinstance(mod, ItemModifier):
                raise Exception
            for part, pmod in mod.parts.items():
                p[part] += pmod

        for part, _ in self._parts.items():
            self._parts[part].set_bonus(p[part])
        return self._parts

    @property
    def attributes(self) -> dict[Attribute, Scale]:
        p = {i: 0.0 for i in self._attributes}

        for mod in self.modifiers:
            if isinstance(mod, ItemModifier):
                raise Exception
            for part, pmod in mod.attributes.items():
                p[part] += pmod
        for part, _ in self._attributes.items():
            self._attributes[part].set_bonus(p[part])

        return self._attributes

    @property
    def scales(self) -> dict[EntityScales, Scale]:
        for type, scale in self._scales.items():
            scale.set_bonus(100 * self.calc_bonus(type.value[2], max_value_bonus=True))
        return self._scales

    def tick(self, time: int) -> None:
        for act in self.queue_actions:
            act.prepare = max(0, act.prepare - time)
            if act.prepare == 0:
                if act.use_slot:
                    act.use_slot.count -= 1
                else:
                    act.cooldown = act.skill.cooldown
                self.effects.extend([e.new_instance for e in act.skill.effects])

        self.queue_actions = [a for a in self.queue_actions if not a.prepare]
        for effect in self.effects:
            if not effect.effect.interval:
                self.apply_effect(effect)
            elif not effect.time % effect.effect.interval:
                self.apply_effect(effect)
                effect.time = max(0, effect.time - time)

        self.effects = [e for e in self.effects if not e.time]

        for skill in self.skills.learned:
            skill.cooldown = max(0, skill.cooldown - time)

    @property
    def minimal_tick(self) -> list[int]:
        # TODO: Remove this
        # timers = []
        # for act in self.queue_actions:
        #     timers.append((0, act, act.prepare))
        # for effect in self.effects:
        #     timers.append((1, effect, effect.effect.interval))
        # for skill in self.actions:
        #     timers.append((2, skill, skill.cooldown))
        # print(timers)
        timers: list[int] = []
        for act in self.queue_actions:
            timers.append(act.prepare)
        for effect in self.effects:
            timers.append(effect.effect.interval)
        for skill in self.actions:
            timers.append(skill.cooldown)
        return timers

    def use(self, skill: SkillState, target: Entity) -> float | Item | None:
        mana_cost = skill.skill.cost_mp * self.calc_bonus(Attribute.WISDOM)

        if mana_cost > self.scales[EntityScales.MP].value:
            return mana_cost

        slot = None
        if skill.skill.cost_item:
            if isinstance(skill.skill.cost_item, ItemTag):
                raise Exception("Not supported yet")
            slot = self.inventory.find(skill.skill.cost_item)
            if not slot:
                return skill.skill.cost_item
        if slot:
            slot.count -= 1
        self.scales[EntityScales.MP] += -mana_cost

        skill.prepare = round(skill.skill.prepare_time * self.calc_bonus(Attribute.WISDOM))
        skill.cooldown = skill.skill.cooldown + skill.prepare
        target.queue_actions.append(skill)
        return None

    def apply_effect(self, effect: EffectState) -> None:
        if effect.effect.target == TargetType.ITEM:
            raise ValueError
        if any(isinstance(i, ItemModifier) for i in effect.effect.modifiers):
            raise ValueError

        for mod in effect.effect.modifiers:
            if isinstance(mod, ItemModifier):
                raise Exception("Not supported yet")
            for part, val in mod.parts.items():
                self.parts[part] += val
            for sc, val in mod.scales.items():
                self.scales[sc] += val


class TimeCluster:
    def __init__(self, *entities: Entity):
        self.entities: list[Entity] = list(entities)

    @property
    def minimal_tick(self) -> Any | Literal[0]:
        timers: list[int] = []
        for e in self.entities:
            timers.extend(e.minimal_tick)
        if timers := [i for i in timers if i]:
            return min(timers)
        return 0

    def tick(self, time: int) -> None:
        for e in self.entities:
            e.tick(time)

    def auto(self) -> None:
        self.tick(self.minimal_tick)
