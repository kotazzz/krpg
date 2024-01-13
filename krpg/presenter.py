from __future__ import annotations

from itertools import groupby
from typing import TYPE_CHECKING, Callable, Optional

from krpg.attributes import Attributes
from krpg.entity import Entity
from krpg.inventory import Item, ItemType, Slot

if TYPE_CHECKING:
    from krpg.game import Game


class Presenter:
    """
    The Presenter class is responsible for presenting game-related information to the user interface.
    It contains methods for displaying player and entity statistics, inventory items, and other game-related information.
    """

    def __init__(self, game: Game):
        self.game = game

    def create_bar(self, value, maximum, color="green", width=15):
        """
        Generates a progress bar string based on the given value and maximum.

        Args:
            value (float): The current value.
            maximum (float): The maximum value.
            color (str, optional): The color of the progress bar. Defaults to "green".
            width (int, optional): The width of the progress bar. Defaults to 15.

        Returns:
            str: The generated progress bar string.
        """
        symlen = int(value / maximum * width) if maximum else 0
        return f"[white][[{color}]{'|'*symlen}{' '*(width-symlen)}[white]][/]"

    def get_stats(self, source: Entity | Item):
        """
        Generates a string representation of the statistics of the given entity or item.

        Args:
            source (Entity | Item): The entity or item to get the statistics from.

        Returns:
            str: The generated statistics string.
        """

        def _get(obj: Attributes, free: bool):
            stats: list[tuple[str, str]] = [
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
                val = getattr(obj, stat)
                full_stats += f"[b {c}]{stat[0].upper():>2}{val}"

            if free:
                return full_stats + f"   [b white]F{obj.free:>2}[/]"
            return full_stats

        if isinstance(source, Entity):
            return _get(source.attributes, True)
        return _get(source.attributes, False)

    def presense(self, e: Entity, minimal=False):
        """
        Presents the information of the given entity to the user interface.

        Args:
            e (Entity): The entity to present.
            minimal (bool, optional): Whether to display minimal information. Defaults to False.
        """
        console = self.game.console

        if minimal:
            name = f"[bold white]{e.name}[/][white]:"
            hp = f"{self.create_bar(e.hp, e.max_hp)} [cyan]HP={e.hp:.2f}/{e.max_hp:.2f}"
            attack = f"[red]A={e.attack:.2f} [blue]D={e.defense:.2f}[/]"
            console.print(f"{name} {attack} {hp}")
        else:
            stats = (
                f"[cyan]HP={e.hp:.2f}/{e.max_hp:.2f} {self.create_bar(e.hp, e.max_hp, 'green')}\n"
                f"[red]A={e.attack:.2f} [blue]D={e.defense:.2f}\n" + self.get_stats(e)
            )
            console.print(f"[bold white]{e.name}[/]\n{stats}")

    def presenses(self, entities: list[Entity]):
        """
        Presents the information of multiple entities to the user interface.

        Args:
            entities (list[Entity]): The list of entities to present.
        """
        console = self.game.console
        nl = max(len(e.name) for e in entities)
        al = max(len(f"{e.attack:.2f}") for e in entities)
        dl = max(len(f"{e.defense:.2f}") for e in entities)
        hl = max(len(f"{e.hp:.2f}") for e in entities)
        ml = max(len(f"{e.max_hp:.2f}") for e in entities)

        for e in entities:
            name = f"[bold white]{e.name:<{nl}}[white]:"
            hp = f"{self.create_bar(e.hp, e.max_hp)} [cyan]HP={e.hp:<{hl}.2f}/{e.max_hp:<{ml}.2f}"
            attack = f"[red]A={e.attack:<{al}.2f} [blue]D={e.defense:<{dl}.2f}[/]"
            stats = self.get_stats(e)
            console.print(f"{stats} {name} {attack} {hp}")

    def show_item(
        self, slot: Slot, show_amount=True, additional: Optional[Callable] = None
    ):
        """
        Generates a string representation of the item in the given slot.

        Args:
            slot (Slot): The slot containing the item.
            show_amount (bool, optional): Whether to display the amount of the item. Defaults to True.
            additional (callable, optional): Additional information to display about the item. Defaults to None.

        Returns:
            str: The generated string representation of the item.
        """
        game = self.game

        if slot.empty:
            return "[yellow]-[/] "
        item = game.bestiary.get_item(slot.id)
        text = ""
        if show_amount:
            text += f"[white]{slot.amount}x"
        text += f"[green]{item.name}[/] "
        if additional:
            text += additional(item)
        return text

    def presence_item(self, item: Item):
        """
        Presents the information of the given item to the user interface.

        Args:
            item (Item): The item to present.
        """

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

    def show_inventory(
        self,
        show_number=False,
        show_amount=True,
        allow: Optional[list[ItemType]] = None,
        inverse: bool = False,
    ):
        """
        Presents the player's inventory to the user interface.

        Args:
            show_number (bool, optional): Whether to display numbers for each item. Defaults to False.
            show_amount (bool, optional): Whether to display the amount of each item. Defaults to True.
            allow (list[ItemType], optional): The list of allowed item types to display. Defaults to None.
            inverse (bool, optional): Whether to display items not in the allowed list. Defaults to False.
        """
        console = self.game.console
        inventory = self.game.player.inventory
        console.print("[bold green]Инвентарь[/]")
        grouped_slots = groupby(inventory.slots, lambda i: i.type)
        counter = 1
        for slot_type, slots in grouped_slots:
            if allow:
                # whitelist
                if not inverse and slot_type not in allow:
                    continue
                # blacklist
                if inverse and slot_type in allow:
                    continue
            console.print("[yellow b]" + ItemType.description(slot_type), end=" ")
            for slot in slots:
                if show_number:
                    console.print(f"[blue]\\[{counter}][/]", end="")
                    counter += 1
                console.print(self.show_item(slot, show_amount), end="")
            console.print()

    def __repr__(self):
        return "<Presenter>"
