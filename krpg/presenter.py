from __future__ import annotations
from krpg.entity import Entity

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from krpg.game import Game
    
class Presenter:
    def __init__(self, game: Game):
        self.game = game
    
    
    def bar(self,value, maximum, color="green", width=15):
        symlen = int(value / maximum * width) if maximum else 0
        return f"[white][[{color}]{'|'*symlen}{' '*(width-symlen)}[white]][/]"
    
    def get_stats(self, entity: Entity):
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
                val = getattr(entity.attrib, stat)
                full_stats += f"[b {c}]{stat[0].upper()}{val}"
        return full_stats + f"   [b white]F{entity.attrib.free}[/]"

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
                f"[red]A={e.attrib.attack:.2f} [blue]D={e.attrib.defense:.2f}\n" + self.get_stats(e)
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
    
    def __repr__(self):
        return "<Presenter>"