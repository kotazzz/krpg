from __future__ import annotations

from typing import TYPE_CHECKING

from rich.tree import Tree

from krpg.actions import action
from krpg.entity import Entity
from krpg.events import Events
from krpg.executer import executer_command
from krpg.inventory import Item, ItemType, Slot
from krpg.world import Location

if TYPE_CHECKING:
    from krpg.game import Game


class Player(Entity):
    """
    Represents a player in the game.

    Args:
        game (Game): The game instance.

    Attributes:
        game (Game): The game instance.
        money (int): The amount of money the player has.
        inventory (Inventory): The player's inventory.
        attributes (Attributes): The player's attributes.
        hp (int): The current health points of the player.
        max_hp (int): The maximum health points of the player.

    Methods:
        pickup(item: Item, amount: int) -> bool: Picks up an item from the game world.
        give_command(game: Game, item_id: str, amount: int = 1): Gives an item to the player.
        add_money(amount: int): Adds money to the player's balance.
        add_money_command(game: Game, money: int): Adds money to the player's balance.
        add_free(amount: int): Adds free attribute points to the player.
        add_free_command(game: Game, free: int): Adds free attribute points to the player.
        heal(amount: int): Heals the player by the specified amount.
        heal_command(game: Game, amount: int): Heals the player by the specified amount.
        damage(amount: int): Damages the player by the specified amount.
        damage_command(game: Game, amount: int): Damages the player by the specified amount.
        apply(item: Item): Applies the effects of an item to the player.
        apply_command(game: Game, item_id: str): Applies the effects of an item to the player.
        has(item: Item | str) -> Slot | bool: Checks if the player has a specific item.
        require_item(item_id: str, amount: int = 1, take: bool = True) -> bool: Checks if the player has a required item.
        require_item_command(game: Game, item_id: str, amount: int = 1): Checks if the player has a required item.
        move_command(game: Game, new_loc): Moves the player to a new location.
        action_look(game: Game): Performs the "look" action.
        action_pickup(game: Game): Performs the "pickup" action.
        action_map(game: Game): Performs the "map" action.
        action_me(game: Game): Performs the "me" action.
        action_go(game: Game): Performs the "go" action.
        action_inventory(game: Game): Performs the "inventory" action.
        action_upgrade(game: Game): Performs the "upgrade" action.
    """

    def __init__(self, game: Game):
        self.game = game
        super().__init__(game, "Player")
        self.game.add_saver("player", self.save, self.load)
        self.game.add_actions(self)
        self.game.executer.add_extension(self)

    def pickup(self, item: Item, amount: int):
        total = self.inventory.count(item.id) + amount
        self.game.events.dispatch(Events.PICKUP, item=item, amount=amount, total=total)
        return self.inventory.pickup(item, amount)

    @executer_command("give")
    @staticmethod
    def give_command(game: Game, item_id: str, amount: int = 1):
        item = game.bestiary.get_item(item_id)
        amount = int(amount)
        if not item:
            raise ValueError(f"Unknown item {item_id}")
        remain = game.player.pickup(item, amount)
        if remain:
            game.console.print(f"[red]Вы не смогли подобрать {remain}x{item.name}[/]")
            game.world.drop(item_id, remain)

    def add_money(self, amount):
        if not amount:
            return
        self.money += amount
        kw = {"amount": amount, "new_balance": self.money}

        if amount > 0:

            self.game.events.dispatch(Events.ADD_MONEY, **kw)
        else:
            self.game.events.dispatch(Events.REMOVE_MONEY, **kw)

    @executer_command("add_money")
    @staticmethod
    def add_money_command(game: Game, money):
        money = int(money)
        game.player.add_money(money)

    # TODO: Optimize it
    def add_free(self, amount):
        if not amount:
            return
        self.attributes.free += amount
        kw = {"amount": amount, "new_balance": self.attributes.free}
        if amount > 0:
            self.game.events.dispatch(Events.ADD_FREE, **kw)
        else:
            self.game.events.dispatch(Events.REMOVE_FREE, **kw)

    @executer_command("add_free")
    @staticmethod
    def add_free_command(game: Game, free: int):
        free = int(free)
        game.player.add_free(free)

    def heal(self, amount):
        if amount <= 0:
            return self.damage(-amount)
        amount = min(amount, self.max_hp - self.hp)
        self.hp += amount
        self.game.events.dispatch(Events.HEAL, amount=amount)

    @executer_command("heal")
    @staticmethod
    def heal_command(game: Game, amount):
        amount = int(amount)
        game.player.heal(amount)

    def damage(self, amount):
        if amount <= 0:
            return self.heal(-amount)
        amount = min(amount, self.hp)
        self.hp -= amount
        self.game.events.dispatch(Events.DAMAGE, amount=amount)
        if self.hp <= 0:
            self.game.events.dispatch(Events.DEAD)

    @executer_command("damage")
    @staticmethod
    def damage_command(game: Game, amount):
        amount = int(amount)
        game.player.damage(amount)

    def apply(self, item: Item):
        effects = item.effects
        for name, val in effects.items():
            if name == "hp":
                self.heal(val)  # TODO: more effects
            else:
                raise ValueError(f"Unknown effect {name}")

    @executer_command("apply")
    @staticmethod
    def apply_command(game: Game, item_id: str):
        item = game.bestiary.get_item(item_id)
        if not item:
            raise ValueError(f"Unknown item {item_id}")
        game.player.apply(item)

    def has(self, item: Item | str, amount: int = 1) -> Slot | bool:
        item = item.id if isinstance(item, Item) else item
        for slot in self.inventory.slots:
            if slot.id == item and slot.amount >= amount:
                return slot
        return False

    def require_item(self, item_id: str, amount: int = 1, take: bool = True) -> bool:
        game = self.game
        # slot = game.player.has(item_id)
        # # if not slot:
        # #     raise ValueError(f"Unknown item {item_id}")
        # assert isinstance(slot, Slot), f"Unknown item {item_id}"
        for slot in self.inventory.slots:
            if slot.id == item_id:
                slot = slot
                break
        else:
            raise ValueError(f"Unknown item {item_id}")
        if slot.amount < amount:
            return False
        if take:
            if amount == slot.amount:
                slot.clear()
            else:
                slot.amount -= amount
        return True

    @executer_command("require_item")
    @staticmethod
    def require_item_command(game: Game, item_id: str, amount: int = 1):
        amount = int(amount)
        game.player.require_item(item_id, amount)

    @executer_command("move")
    @staticmethod
    def move_command(game: Game, new_loc):
        game.world.set(new_loc)

    @action("look", "Информация об этом месте", "Информация")
    @staticmethod
    def action_look(game: Game):
        location = game.world.current
        subs = game.world.get_road(location)
        game.console.print(
            f"[bold green]Ваша позиция: [bold white]{location.name} - {location.description}\n[green]Доступно:[/]"
        )
        if not subs:
            game.console.print("  [bold red]Нет доступных направлений[/]")
        for sub in subs:
            game.console.print(f"  [bold blue]{sub.name}[/]")
        game.console.print()

        game.console.print("[bold green]Предметы[/]")
        if not location.items:
            game.console.print("  [bold red]Ничего интересного[/]")
        for item_id, count in location.items:
            item = game.bestiary.get_item(item_id)
            game.console.print(f"  [white]{count}x[green]{item.name}[/]")
        game.console.print()

        game.console.print("[bold green]Люди[/]")
        npc = game.npc_manager.get_npcs(location.id)
        if not npc:
            game.console.print("  [bold red]Никого нет[/]")
        for npc in npc:
            game.console.print(f"  [bold blue]{npc.name}[/]")
        game.console.print()

    @action("pickup", "Подобрать предмет", "Действия")
    @staticmethod
    def action_pickup(game: Game):
        location = game.world.current
        variants = [(c, game.bestiary.get_item(i)) for i, c in location.items]
        select: tuple[int, Item] = game.console.menu(
            2,
            variants,
            "e",
            lambda o: f"[white]{o[0]}x[blue]{o[1].name}",
            title="Предметы",
        )
        if select:
            selected_id = select[1].id
            remain = game.player.pickup(select[1], select[0])
            game.world.take(location, selected_id, remain)
            game.clock.wait(2)

    @action("map", "Информация о карте", "Информация")
    @staticmethod
    def action_map(game: Game):
        tree = Tree(f"[green b]{game.world.current.name} [/][blue] <-- Вы тут[/]")
        visited = [game.world.current]

        def populate(tree: Tree, location: Location):
            for loc in game.world.get_road(location):
                if loc not in visited:
                    visited.append(loc)
                    sub = tree.add(f"[green]{loc.name}")
                    populate(sub, loc)

        populate(tree, game.world.current)
        game.console.print(tree)

    @action("me", "Информация о себе", "Игрок")
    @staticmethod
    def action_me(game: Game):
        game.presenter.presense(game.player)
        game.console.print(f"[yellow b]Баланс[/]: [yellow]{game.player.money}")

    @action("go", "Отправиться", "Действия")
    @staticmethod
    def action_go(game: Game):
        w = game.world
        roads = w.get_road(w.current)
        new_loc: Location = game.console.menu(
            3, roads, "e", lambda o: o.name, title="Локации"
        )
        if new_loc:
            if w.set(new_loc):
                game.console.print(f"[yellow]Вы пришли в {new_loc.name}")

    @action("inventory", "Управление инвентарем", "Игрок")
    @staticmethod
    def action_inventory(game: Game):
        console = game.console
        inventory = game.player.inventory
        bestiary = game.bestiary
        presenter = game.presenter
        console.print(
            "[bold green]Управление инвентарем. Введите номер слота для управления им[/]\n"
            "  [green]e[white] - выход[/]"
        )

        while True:
            game.presenter.show_inventory(True)
            slot: Slot = console.menu(
                2, inventory.slots, "e", lambda x: presenter.show_item(x), display=False
            )
            if not slot:
                break
            if slot.empty:
                console.print(f"Слот пуст!")
                continue

            console.print(
                f"[bold green]Управление предметом: {presenter.show_item(slot)}[/]\n"
                "  [green]i[white] - информация[/]\n"
                "  [green]w[white] - надеть/снять[/]\n"
                "  [green]u[white] - использовать[/]\n"
                "  [green]d[white] - выкинуть[/]\n"
                "  [green]e[white] - отмена[/]"
            )
            item = bestiary.get_item(slot.id)
            op = console.checked(3, lambda x: x in "iwude")
            if op == "e":
                continue
            if op == "i":
                presenter.presence_item(item)
            elif op == "w":
                if slot.type == ItemType.ITEM and item.type != ItemType.ITEM:
                    slots = inventory.get(item.type, only_empty=True)
                    if slots:
                        slots[0][1].swap(slot)
                        console.print(f"[green]Предмет надет[/]")
                    else:
                        console.print(f"[red]Нет доступных слотов[/]")
                elif slot.type != ItemType.ITEM:
                    slots = inventory.get(ItemType.ITEM, only_empty=True)
                    if slots:
                        slots[0][1].swap(slot)
                        console.print(f"[green]Предмет снят[/]")
                    else:
                        console.print(f"[red]Нет доступных слотов[/]")
                elif slot.type == ItemType.ITEM and item.type == ItemType.ITEM:
                    console.print(f"[red]Вы не можете это надеть")
            elif op == "u":
                if item.effects:
                    game.player.apply(item)
                    slot.amount -= 1
                else:
                    console.print(f"[red]Вы не можете это использовать")
            elif op == "d":
                if game.bestiary.get_item(slot.id).throwable:
                    game.world.drop(slot.id, slot.amount)
                    slot.clear()
                    console.print(f"[green]Предмет успешно выброшен[/]")
                else:
                    console.print(f"[red]Вы не можете это выбросить")

    @action("upgrade", "Улучшить персонажа", "Действия")
    @staticmethod
    def action_upgrade(game: Game):
        # [red]S[/], [green]P[/], [blue]E[/], [yellow]C[/], [magenta]I[/], [cyan]A[/], [white]W[/]
        c = game.console
        a = game.player.attributes
        stats: list[tuple[str, str, str]] = [
            ("red", "strength", "сила"),
            ("green", "perception", "восприятие"),
            ("blue", "endurance", "выносливость"),
            ("yellow", "charisma", "харизма"),
            ("magenta", "intelligence", "интеллект"),
            ("cyan", "agility", "ловкость"),
            ("white", "wisdom", "мудрость"),
        ]
        c.print("[green]Добро пожаловать в мастер распределения характеристик!")
        c.print("Введите [red]exit[/] для завершения распределения.")
        c.print("Введите первую букву характеристики, которую хотите повысить.")
        chars = {i[1][0]: i[1] for i in stats}
        while a.free > 0:
            c.print(f"Вам доступно [bold white]{a.free}[/] очков.")
            for col, name, text in stats:
                c.print(
                    f"[{col} b]({name[0].upper()})[/] [{col}]{name}[/] - {text}: [{col}]{getattr(a, name)}[/]"
                )
            char = c.prompt(2).lower()
            if char == "exit":
                break
            elif char in chars:
                a.update(**{chars[char]: 1}, set=False)
            else:
                continue
            a.free -= 1
        c.print("[green]Распределение завершено.[/]")
