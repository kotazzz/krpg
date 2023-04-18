from __future__ import annotations
from krpg.actions import action
from krpg.entity import Entity

from typing import TYPE_CHECKING
from rich.tree import Tree
from krpg.executer import executer_command
from krpg.inventory import Item

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
        self.game.events.dispatch("pickup", item=item, amount=amount)
        return self.inventory.pickup(item, amount)

    def add_money(self, amount):
        if not amount:
            return
        if amount > 0:
            event = "add_money"
        else:
            event = "remove_money"
        self.money += amount
        self.game.events.dispatch(event, amount=amount, new_balance=self.money)

    @executer_command("add_money")
    def add_money_command(game: Game, money):
        money = int(money)
        game.player.add_money(money)

    # TODO: Optimize it
    def add_free(self, amount):
        if not amount:
            return
        if amount > 0:
            event = "add_free"
        else:
            event = "remove_free"
        self.attrib.free += amount
        self.game.events.dispatch(event, amount=amount, new_balance=self.attrib.free)

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
        c = game.console
        # TODO: TODO
        c.print(f"[red b]Пока тут ничего нет")

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
