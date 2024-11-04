from attr import field
import attr
from krpg.entity.effects import Effect
from krpg.entity.entity import Entity
from krpg.entity.inventory import Item
from krpg.entity.skills import Skill
from krpg.entity.utils import _add, _get_by_id


@attr.s(auto_attribs=True)
class Bestiary:
    skills: list[Skill] = field(factory=list)
    items: list[Item] = field(factory=list)
    effects: list[Effect] = field(factory=list)
    entities: list[Entity] = field(factory=list)

    def add_skill(self, skill: Skill):
        _add(self.skills, skill)

    def add_item(self, item: Item):
        _add(self.items, item)

    def add_effect(self, effect: Effect):
        _add(self.effects, effect)

    def add_entity(self, entity: Entity):
        _add(self.entities, entity)

    def get_skill_by_id(self, skill_id: str):
        return _get_by_id(self.skills, skill_id)

    def get_item_by_id(self, item_id: str):
        return _get_by_id(self.items, item_id)

    def get_effect_by_id(self, effect_id: str):
        return _get_by_id(self.effects, effect_id)

    def get_entity_by_id(self, entity_id: str):
        return _get_by_id(self.entities, entity_id)
