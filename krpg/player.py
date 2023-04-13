from __future__ import annotations
from krpg.actions import action
from krpg.entity import Entity

from typing import TYPE_CHECKING
from rich.tree import Tree

from krpg.world import Location

if TYPE_CHECKING:
    from krpg.game import Game


class Player(Entity):
    def __init__(self, game: Game):
        self.game = game
        super().__init__("Player")
        self.game.add_saver("player", self.save, self.load)
        self.game.add_actions(self)
    
    @action("me", "Информация о себе", "Игрок")
    def action_me(game: Game):
        print(game.player.attrib.calc_hp())
        
    @action("map", "Информация о карте", "Игрок")
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
    
    @action("go", "Отправиться", "Игрок")
    def action_go(game: Game):
        w = game.world
        roads =  w.get_road(w.current)
        new_loc: Location = game.console.menu(3,roads, 'e', lambda o: o.name)
        if new_loc:
            w.set(new_loc)
            game.console.print(f'[yellow]Вы пришли в {new_loc.name}')
    
    