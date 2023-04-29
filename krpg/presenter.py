from __future__ import annotations
from itertools import groupby
from krpg.attributes import Attributes
from krpg.entity import Entity

from typing import TYPE_CHECKING

from krpg.inventory import Item, ItemType, Slot

if TYPE_CHECKING:
    from krpg.game import Game


class Presenter:
    def __init__(self, game: Game):
        self.game = game

    def bar(self, value, maximum, color="green", width=15):
        symlen = int(value / maximum * width) if maximum else 0
        return f"[white][[{color}]{'|'*symlen}{' '*(width-symlen)}[white]][/]"

    def get_stats(self, entity: Entity|Item):
        def _get(attrib: Attributes, free: bool):
            stats: tuple[str, str] = [
                ("red", "strength"),
                ("green", "perception"),
                ("blue", "endurance"),
                ("yellow", "charisma"),
                ("magenta", "intelligence"),
                ("cyan", "agility"),
                ("white", "wisdom"),
            ]
            full_stats = ""
            for c, stat in stats:
                val = getattr(attrib, stat)
                full_stats += f"[b {c}]{stat[0].upper()}{val}"
            
            if free:
                return full_stats + f"   [b white]F{entity.attrib.free}[/]"
            return  full_stats
        
        if isinstance(entity, Entity):
            return _get(entity.attrib, True)
        return _get(entity.attributes, False)

    def presense(self, e: Entity, minimal=False):
        console = self.game.console

        if minimal:
            name = f"[bold white]{e.name}[/][white]:"
            hp = f"{self.bar(e.hp, e.attrib.max_hp)} [cyan]HP={e.hp:.2f}/{e.attrib.max_hp:.2f}"
            attack = f"[red]A={e.attrib.attack:.2f} [blue]D={e.attrib.defense:.2f}[/]"
            console.print(f"{name} {attack} {hp}")
        else:
            stats = (
                f"[cyan]HP={e.hp:.2f}/{e.attrib.max_hp:.2f} {self.bar(e.hp, e.attrib.max_hp, 'green')}\n"
                f"[red]A={e.attrib.attack:.2f} [blue]D={e.attrib.defense:.2f}\n"
                + self.get_stats(e)
            )
            console.print(f"[bold white]{e.name}[/]\n{stats}")

    def presenses(self, entities: list[Entity]):
        console = self.game.console
        nl = max([len(e.name) for e in entities])
        al = max([len(f"{e.attrib.attack:.2f}") for e in entities])
        dl = max([len(f"{e.attrib.defense:.2f}") for e in entities])
        hl = max([len(f"{e.hp:.2f}") for e in entities])
        ml = max([len(f"{e.attrib.max_hp:.2f}") for e in entities])

        for e in entities:
            name = f"[bold white]{e.name:<{nl}}[0 white]:"
            hp = f"{self.bar(e.hp, e.attrib.max_hp)} [cyan]HP={e.hp:<{hl}.2f}/{e.attrib.max_hp:<{ml}.2f}"
            attack = f"[red]A={e.attrib.attack:<{al}.2f} [blue]D={e.attrib.defense:<{dl}.2f}[/]"
            stats = self.get_stats(e)
            console.print(f"{stats} {name} {attack} {hp}")
    
    def show_item(self, slot: Slot,show_amount=True):
        game = self.game
        
        if slot.empty:
            return "[yellow]-[/] "
        else:
            item = game.bestiary.get_item(slot.id)
            text = ""
            if show_amount:
                text += f"[white]{slot.amount}x"
            text += f"[green]{item.name}[/] "
            return text
    
    def presence_item(self, item: Item):
        
        def get_effects_string(effects: dict[str, int]) -> str:
            if not effects:
                return "[b red]Эффектов нет[/]\n"
            result = "[b red]Эффекты[/]:\n"
            for key, value in effects.items():
                result += f"    {key}: {value}\n"
            return result


        
        item_type_info = f"[b green]Тип[/]: {ItemType.description(item.type)}\n"
        effects_info = get_effects_string(item.effects)
        sell_info = (
            f"[b yellow]Цена продажи[/]: {item.sell}\n"
            if item.sell > 0
            else "[b yellow]Ничего не стоит[/]\n"
        )
        cost_info = (
            f"[b yellow]Цена покупки[/]: {item.cost}\n"
            if item.cost > 0
            else "[b yellow]Не продается[/]\n"
        )
        stats_info = f"[white b]Характеристики[/]: {self.get_stats(item)}\n"
        result = f"[purple b]{item.name}[/] - {item.description}\n"
        result += item_type_info
        result += stats_info
        result += effects_info
        result += sell_info
        result += cost_info
        self.game.console.print(result)
    
    def show_inventory(self, show_number=False,show_amount=True, allow: list[ItemType]=None, inverse: bool=False):
        console = self.game.console
        inventory = self.game.player.inventory
        console.print("[bold green]Инвентарь[/]")
        last = None
        slots = groupby(inventory.slots, lambda i: i.type)
        counter = 1
        for slot_type, slots in slots:
            if allow:
                # whitelist
                if not inverse and slot_type not in allow:
                    continue
                # blacklist
                if inverse and slot_type in allow:
                    continue
            console.print("[yellow b]"+ItemType.description(slot_type), end=" ")
            for slot in slots:
                if show_number:
                    console.print(f"[blue]\[{counter}][/]", end="")
                    counter += 1
                console.print(self.show_item(slot, show_amount), end="")
            console.print()
    def __repr__(self):
        return "<Presenter>"
