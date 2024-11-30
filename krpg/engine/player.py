from __future__ import annotations
from typing import TYPE_CHECKING

from krpg.actions import ActionCategory, ActionManager, action
from krpg.components import component
from krpg.console.entities import render_entity, render_item
from krpg.console.world import render_location_info
from krpg.entity.entity import Entity
from krpg.entity.inventory import Slot, drop, equip


if TYPE_CHECKING:
    from krpg.game import Game

from krpg.console.entities import render_inventory

@component
class Actions(ActionManager):
    @action("me", "Показать информацию о себе", ActionCategory.INFO)
    @staticmethod
    def action_me(game: Game) -> None:
        player = game.player
        player_entity = player.entity
        game.console.print(render_entity(player_entity))

    @action("look", "Посмотреть на местность", ActionCategory.INFO)
    @staticmethod
    def action_look(game: Game) -> None:
        loc = game.world.current_location
        assert loc is not None, "Current location is not set"
        game.console.print(render_location_info(loc))

    @action("inventory", "Посмотреть инвентарь", ActionCategory.PLAYER)
    @staticmethod
    def inventory(game: Game):
        inventory = game.player.entity.inventory
        console = game.console

        console.print(render_inventory(inventory))
        while True: 
            slot: Slot = console.select(
                "Выберите слот: ", {
                    str(i): j for i, j in enumerate(inventory.slots, 1)
                }
            )
            if not slot:
                break
            if slot.empty:
                console.print("[red]Нельзя выбрать пустой слот")
                continue
            assert slot.item

            console.print(
                f"[bold green]Управление предметом: {slot.item.name}[/]\n" # Should never happen    
                "  [green]i[white] - информация[/]\n"
                "  [green]w[white] - надеть/снять[/]\n"
                "  [green]d[white] - выкинуть[/]\n"
                "  [green]e[white] - отмена[/]"
            )
            action = console.select(
                "Выберите действие: ", {"i":"i", "w":"w", "d":"d"}
            )
            if not action:
                break
            if action == "i":
                console.print(render_item(slot.item))
            elif action == "w":
                game.commands.execute(equip(slot))
            elif action == "d":
                def validator(x: str) -> bool:
                    return x.isdigit() and int(x) <= slot.count and int(x) > 0
                
                count = console.prompt(
                    "Количество: ", validator=validator
                )
                game.commands.execute(drop(slot, count))

    @action("pickup", "Поднять предметы на карте", ActionCategory.PLAYER)
    @staticmethod
    def pickup(game: Game):
        loc = game.world.current_location
        assert loc
        console = game.console
        if not loc.items:
            console.print("Нет предметов")
        raise NotImplementedError
    

class Player:
    def __init__(self) -> None:
        self.entity = Entity("player", "Игрок")
