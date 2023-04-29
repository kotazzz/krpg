from __future__ import annotations
from itertools import groupby
from krpg.actions import action
from krpg.entity import Entity

from typing import TYPE_CHECKING
from rich.tree import Tree
from krpg.executer import executer_command
from krpg.inventory import Item, ItemType, Slot

from krpg.events import Events
from krpg.world import Location

if TYPE_CHECKING:
    from krpg.game import Game


class Player(Entity):
    def __init__(self, game: Game):
        self.game = game
        super().__init__("Player")
        self.game.add_saver("player", self.save, self.load)
        self.game.add_actions(self)
        self.game.executer.add_extension(self)

    # Executor and actions

    def pickup(self, item: Item, amount: int):
        self.game.events.dispatch(Events.PICKUP, item=item, amount=amount)
        return self.inventory.pickup(item, amount)

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
    def add_money_command(game: Game, money):
        money = int(money)
        game.player.add_money(money)

    # TODO: Optimize it
    def add_free(self, amount):
        if not amount:
            return
        self.attrib.free += amount
        kw = {"amount": amount, "new_balance": self.attrib.free}
        if amount > 0:
            self.game.events.dispatch(Events.ADD_FREE, **kw)
        else:
            self.game.events.dispatch(Events.REMOVE_FREE, **kw)

    def heal(self, amount):
        amount = min(amount, self.attrib.max_hp - self.hp)
        self.hp += amount
        self.game.events.dispatch(Events.HEAL, amount=amount)

    def apply(self, item: Item):
        effects = item.effects
        for name, val in effects.items():
            if name == "hp":
                self.heal(val)

    @executer_command("add_free")
    def add_free_command(game: Game, free):
        free = int(free)
        game.player.add_free(free)

    @executer_command("move")
    def move_command(game: Game, new_loc):
        game.world.set(new_loc)

    # Actions
    @action("look", "Информация об этом месте", "Информация")
    def action_look(game: Game):
        location = game.world.current
        sub = game.world.get_road(location)
        game.console.print(
            f"[bold green]Ваша позиция: [bold white]{location.name} - {location.description}\n[green]Доступно:[/]"
        )
        if not sub:
            game.console.print("  [bold red]Нет доступных направлений[/]")
        for sub in sub:
            game.console.print(f"  [bold blue]{sub.name}[/]")
        game.console.print()

        game.console.print("[bold green]Предметы[/]")
        if not location.items:
            game.console.print("  [bold red]Ничего интересного[/]")
        for item_id, count in location.items:
            item = game.bestiary.get_item(item_id)
            game.console.print(f"  [white]{count}x[green]{item.name}[/]")
        game.console.print()

    @action("pickup", "Подобрать предмет", "Действия")
    def command_pickup(game: Game):
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
    def action_map(game: Game):
        game.console.print(f"[green b]Вы тут: {game.world.current.name}")
        tree = Tree("[green]Карта мира[/]")
        visited = []

        def populate(tree: Tree, location: Location):
            for loc in game.world.get_road(location):
                if loc not in visited:
                    visited.append(loc)
                    sub = tree.add(loc.name)
                    populate(sub, loc)

        populate(tree, game.world.current)
        game.console.print(tree)

    @action("me", "Информация о себе", "Игрок")
    def action_me(game: Game):
        game.presenter.presense(game.player)
        game.console.print(f"[yellow b]Баланс[/]: [yellow]{game.player.money}")

    @action("go", "Отправиться", "Действия")
    def action_go(game: Game):
        w = game.world
        roads = w.get_road(w.current)
        new_loc: Location = game.console.menu(
            3, roads, "e", lambda o: o.name, title="Локации"
        )
        if new_loc:
            w.set(new_loc)
            game.console.print(f"[yellow]Вы пришли в {new_loc.name}")

    @action("inventory", "Управление инвентарем", "Игрок")
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
                game.world.drop(slot.id, slot.amount)
                slot.clear()
                console.print(f"[green]Предмет успешно выброшен[/]")

    @action("upgrade", "Улучшить персонажа", "Действия")
    def action_upgrade(game: Game):
        # [red]S[/], [green]P[/], [blue]E[/], [yellow]C[/], [magenta]I[/], [cyan]A[/], [white]W[/]
        c = game.console
        a = game.player.attrib
        stats: tuple[str, str, str] = [
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
                a.update(**{chars[char]: 1})
            else:
                continue
            a.free -= 1
        c.print("[green]Распределение завершено.[/]")
