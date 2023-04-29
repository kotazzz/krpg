from typing import List
from krpg.attributes import Attributes

from krpg.inventory import Item, ItemType

def get_effects_string(effects: dict[str, int]) -> str:
    if not effects:
        return "[red]Эффектов нет[/]\n"
    result = "[red]Эффекты[/]:\n"
    for key, value in effects.items():
        result += f"    {key}: {value}\n"
    return result

def get_stats(item: Item) -> str:
    attributes = item.attributes
    stats = f"[blue]Максимум[/]: {item.stack}\n"
    stats += f"[white]Аттрибуты[/]:\n"
    stats += f"    Сила: {attributes.strength}\n"
    stats += f"    Мудрость: {attributes.wisdom}\n"
    stats += f"    Выносливость: {attributes.endurance}\n"
    stats += f"    Ловкость: {attributes.agility}\n"
    stats += f"    Интеллект: {attributes.intelligence}\n"
    stats += f"    Харизма: {attributes.charisma}\n"
    stats += f"    Восприятие: {attributes.perception}\n"
    return stats

def get_item_info(item: Item) -> str:
    item_type_info = f"[green]Тип[/]: {ItemType.description(item.type)}\n"
    effects_info = get_effects_string(item.effects)
    sell_info = (
        f"[yellow]Цена продажи[/]: {item.sell}\n"
        if item.sell > 0
        else "[yellow]Ничего не стоит[/]\n"
    )
    cost_info = (
        f"[yellow]Цена покупки[/]: {item.cost}\n"
        if item.cost > 0
        else "[yellow]Не продается[/]\n"
    )
    stats_info = get_stats(item)
    result = f"{item.name} - {item.description}\n"
    result += item_type_info
    result += stats_info
    result += effects_info
    result += sell_info
    result += cost_info
    return result

item = Item(
    id="sword_01",
    name="Клинок Кровавой Клятвы",
    description="Меч, который не извлекает жизненную силу из своих жертв, но дарует своему обладателю жизненные силы",
)
item.attributes = Attributes(strength=10, endurance=5)
item.effects = {"кровотечение": 2, "ярость": 3}
item.cost = 100
from rich import print
print(get_item_info(item))
