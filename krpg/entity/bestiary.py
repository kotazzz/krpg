from attr import field
import attr
from krpg.entity.effects import Effect
from krpg.entity.entity import Entity
from krpg.entity.inventory import Item
from krpg.entity.skills import Skill
from krpg.utils import add, get_by_id


@attr.s(auto_attribs=True)
class Bestiary:
    skills: list[Skill] = field(factory=list)
    items: list[Item] = field(factory=list)
    effects: list[Effect] = field(factory=list)
    entities: list[Entity] = field(factory=list)

    def add_skill(self, skill: Skill) -> None:
        add(self.skills, skill)

    def add_item(self, item: Item) -> None:
        add(self.items, item)

    def add_effect(self, effect: Effect) -> None:
        add(self.effects, effect)

    def add_entity(self, entity: Entity) -> None:
        add(self.entities, entity)

    def get_skill_by_id(self, skill_id: str) -> Skill | None:
        return get_by_id(self.skills, skill_id)

    def get_item_by_id(self, item_id: str) -> Item | None:
        return get_by_id(self.items, item_id)

    def get_effect_by_id(self, effect_id: str) -> Effect | None:
        return get_by_id(self.effects, effect_id)

    def get_entity_by_id(self, entity_id: str) -> Entity | None:
        return get_by_id(self.entities, entity_id)
