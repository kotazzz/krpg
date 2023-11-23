from __future__ import annotations
from krpg.events import Events
from krpg.inventory import Slot
from krpg.actions import Action, action
from typing import TYPE_CHECKING

from zlib import crc32
from krpg.executer import Block, executer_command

if TYPE_CHECKING:
    from krpg.game import Game


class Npc:
    def __init__(
        self,
        id: str,
        name: str,
        description: str,
        state: str,
        location: str,
        actions: dict[str, list[Action]],
    ):
        self.id: str = id
        self.name: str = name
        self.state: str = state
        self.description: str = description
        self.location: str = location
        self.actions: dict[str, list[Action]] = actions  # {state: [actions]}
        self.known: bool = False

    def get_actions(self):
        return self.actions[self.state]

    def save(self):
        return [self.state, self.known]

    def load(self, data):
        self.state, self.known = data

    def __repr__(self) -> str:
        return f"<Npc name={self.name!r} state={self.state!r}>"


class NpcManager:
    """
    Class representing a manager for NPCs in the game.

    Attributes:
    - game (Game): The game instance.
    - npcs (list[Npc]): The list of NPCs.
    - talking (Npc | None): The currently talking NPC.

    Methods:
    - save(): Save the data of all NPCs.
    - load(data): Load the data of all NPCs.
    - get_npcs(location): Get NPCs in a specific location.
    - get_npc(id): Get an NPC by its ID.
    - action_talk(game): Perform the "talk" action with available NPCs.
    - say(name, text): Print a message with the given name and text.
    - say_command(game, *text): Execute the "say" command.
    - ans_command(game, *text): Execute the "ans" command.
    - meet_command(game): Execute the "meet" command.
    - set_state_command(game, state): Execute the "set_state" command.
    - set_state(npc, state): Set the state of an NPC.
    - trade_command(game, block): Execute the "trade" command.
    """

    def __init__(self, game: Game):
        self.game = game
        self.npcs: list[Npc] = []
        self.game.add_saver("npcs", self.save, self.load)
        self.game.add_actions(self)
        self.game.executer.add_extension(self)
        self.talking: Npc | None = None

    def save(self):
        data = {}
        for npc in self.npcs:
            data[npc.id] = npc.save()
        return data

    def load(self, data):
        for npc in self.npcs:
            npc.load(data[npc.id])

    def get_npcs(self, location: str):
        return [npc for npc in self.npcs if npc.location == location]

    def get_npc(self, id: str):
        for npc in self.npcs:
            if npc.id == id:
                return npc
        raise Exception(f"Npc {id} not found")

    @action("talk", "Поговорить с доступными нпс", "Действия")
    def action_talk(game: Game):
        loc = game.world.current
        npcs = game.npc_manager.get_npcs(loc.id)
        sel: Npc = game.console.menu(
            2, npcs, "e", lambda n: n.name, title="Выберите нпс"
        )
        if not sel:
            return
        sel_act: Action = game.console.menu(
            2,
            sel.get_actions(),
            "e",
            lambda a: a.description,
            title="Выберите действие",
        )
        if not sel_act:
            return
        game.npc_manager.talking = sel
        sel_act.callback(game)
        game.npc_manager.talking = None

    def say(self, name, text):
        if name == "???":
            nametag = "[grey]???"
        else:
            hash = crc32(name.encode("utf-8"))
            nametag = f"[#{hash&0xffffff:06x}]{name}"
        text = self.game.executer.process_text(text)
        self.game.console.print(f"{nametag}[white]: {text}")

    @executer_command("say")
    def say_command(game: Game, *text):
        text = " ".join(text)
        npc = game.npc_manager.talking
        game.npc_manager.say(npc.name if npc.known else "???", text)

    @executer_command("ans")
    def ans_command(game: Game, *text):
        text = " ".join(text)
        game.npc_manager.say(game.player.name, text)

    @executer_command("meet")
    def meet_command(game: Game):
        game.npc_manager.talking.known = True
        game.events.dispatch(Events.NPC_MEET, npc_id=game.npc_manager.talking.id)

    @executer_command("set_state")
    def set_state_command(game: Game, state: str):
        game.npc_manager.set_state(game.npc_manager.talking, state)

    def set_state(self, npc: Npc, state: str):
        npc.state = state
        self.game.events.dispatch(Events.NPC_STATE, npc_id=npc.id, state=state)

    @executer_command("trade")
    def trade_command(game: Game, block: Block):
        allowed_sell = block.section.first("sell").args
        allowed_buy = block.section.first("buy").args

        inventory = game.player.inventory
        console = game.console
        presenter = game.presenter
        can_sell = lambda i: i.id in allowed_sell
        can_buy = lambda i: i.id in allowed_buy
        additional = (
            lambda i: f"\[[green]{'S' if can_sell(i) else ' '}[red]{'B' if can_buy(i) else ' '}[cyan]]"
        )
        slot_filter = lambda i: can_sell(i) or can_buy(i)

        slots = list(filter(slot_filter, inventory.slots)) + [
            Slot().set(i, 0.1)
            for i in allowed_buy + allowed_sell
            if i not in (x.id for x in inventory.slots)
        ]

        while True:
            slot: Slot = console.menu(
                2,
                slots,
                "e",
                lambda x: presenter.show_item(x, False, additional),
                display=True,
            )
            if not slot:
                return
            action = console.menu(
                3,
                ((0, "Продать"), (1, "Купить"), (2, "Инфо")),
                "e",
                lambda x: x[1],
                title="Выберите действие",
            )[0]
            if action == "e":
                break
            if action == 0:
                if not can_sell(slot):
                    console.print("[red]Вы не можете продать этот предмет")
                    continue
                amount = console.checked(
                    "[green]Сколько продать?: ", lambda x: x.isdigit()
                )
                amount = int(amount)
                if amount > slot.amount:
                    console.print("[red]У вас нет столько предметов")
                    continue

                if amount == slot.amount:
                    slot.clear()
                else:
                    slot.amount -= amount
                item = game.bestiary.get_item(slot.id)
                money = item.sell * amount
                game.player.add_money(money)
                console.print(
                    f"[green]Вы продали {amount}x{item.name} за {money} монет"
                )

            elif action == 1:
                if not can_buy(slot):
                    console.print("[red]Вы не можете купить этот предмет")
                    continue
                amount = console.checked(
                    "[green]Сколько купить?: ", lambda x: x.isdigit()
                )
                amount = int(amount)
                item = game.bestiary.get_item(slot.id)
                money = item.cost * amount
                if money > game.player.money:
                    console.print("[red]У вас нет столько денег")
                    continue
                game.player.add_money(-money)
                game.player.pickup(slot.id, amount)
            elif action == 2:
                item = game.bestiary.get_item(slot.id)
                presenter.presence_item(item)

    def __repr__(self) -> str:
        return f"<NpcManager n={len(self.npcs)}>"
