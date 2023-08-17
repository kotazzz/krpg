from __future__ import annotations
from krpg.inventory import Slot
from krpg.actions import Action, action
from typing import TYPE_CHECKING

from krpg.executer import Block, executer_command
if TYPE_CHECKING:
    from krpg.game import Game


class Npc:
    def __init__(self, id: str, name: str, description: str, state: str,
                 location: str, actions: dict[str, list[Action]]
                 ):
        self.id: str = id
        self.name: str = name
        self.state: str = state
        self.description: str = description
        self.location: str = location
        self.actions: dict[str, list[Action]] = actions # {state: [actions]}
    def get_actions(self):
        return self.actions[self.state]
    
    def __repr__(self) -> str:
        return f"<Npc name={self.name!r} state={self.state!r}>"
    
class NpcManager:
    def __init__(self, game: Game):
        self.game = game
        self.npcs: list[Npc] = []
        self.game.add_saver("npcs", self.save, self.load)
        self.game.add_actions(self)
        self.game.executer.add_extension(self)
    def save(self):
        pass
    def load(self, data):
        pass
    def get_npcs(self, location: str):
        return [npc for npc in self.npcs if npc.location == location]
    
    @action("talk", "Поговорить с доступными нпс", "Действия")
    def action_talk(game:Game):
        loc = game.world.current
        npcs = game.npc_manager.get_npcs(loc.id)
        sel: Npc = game.console.menu(2, npcs, "e", lambda n: n.name, title="Выберите нпс")
        if not sel:
            return
        sel_act: Action = game.console.menu(2, sel.get_actions(), "e", lambda a: a.description, title="Выберите действие")
        if not sel_act:
            return 
        sel_act.callback(game)
    @executer_command("trade")
    def trade_command(game: Game, block: Block):
        allowed_sell = block.section.first("sell").args
        allowed_buy = block.section.first("buy").args
        
        inventory = game.player.inventory
        console = game.console
        presenter = game.presenter
        can_sell = lambda i: i.id in allowed_sell
        can_buy = lambda i: i.id in allowed_buy
        additional = lambda i: f"\[[green]{'S' if can_sell(i) else ' '}[red]{'B' if can_buy(i) else ' '}[cyan]]"
        slot_filter = lambda i: can_sell(i) or can_buy(i)
        
        slots = list(filter(slot_filter, inventory.slots)) + [Slot().set(i, 0.1) for i in allowed_buy+allowed_sell if i not in (x.id for x in inventory.slots)]
        
        while True:
            slot: Slot = console.menu(
                    2, slots, "e", lambda x: presenter.show_item(x, False, additional), display=True
                )
            if not slot:
                return
            action = console.menu(
                3, (
                    (0, "Продать"),
                    (1, "Купить"),
                    (2, "Инфо")
                    ), "e", lambda x: x[1], title="Выберите действие"
            )[0]
            if action == "e":
                break
            if action == 0:
                if not can_sell(slot):
                    console.print("[red]Вы не можете продать этот предмет")
                    continue
                amount = console.checked("[green]Сколько продать?: ", lambda x: x.isdigit())
                amount = int(amount)
                if amount > slot.amount:
                    console.print("[red]У вас нет столько предметов")
                    continue
                
                if amount == slot.amount:
                    slot.clear()
                else:
                    slot.amount -= amount
                item = game.bestiary.get_item(slot.id)
                money = item.sell*amount
                game.player.add_money(money)
                console.print(f'[green]Вы продали {amount}x{item.name} за {money} монет')
                
            elif action == 1:
                if not can_buy(slot):
                    console.print("[red]Вы не можете купить этот предмет")
                    continue
                amount = console.checked("[green]Сколько купить?: ", lambda x: x.isdigit())
                amount = int(amount)
                item = game.bestiary.get_item(slot.id)
                money = item.cost*amount
                if money > game.player.money:
                    console.print("[red]У вас нет столько денег")
                    continue
                game.player.add_money(-money)
                game.player.pickup(slot.id, amount)
            elif action == 2:
                item = game.bestiary.get_item(slot.id)
                presenter.presence_item(item)    
                
                    
        