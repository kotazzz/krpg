from __future__ import annotations

from typing import TYPE_CHECKING

from krpg.entity import Entity

if TYPE_CHECKING:
    from krpg.game import Game


class Presenter:
    def __init__(self, game: Game):
        self.game = game

    def presense(self, e: Entity, minimal=False):
        console = self.game.console

        def bar(value, maximum, color="green", width=15):
            symlen = int(value / maximum * width) if maximum else 0
            return f"[white][[{color}]{'|'*symlen}{' '*(width-symlen)}[white]][/]"

        if minimal:
            console.print(
                f"[bold white]{e.name}[0 white]:"
                f" [red]A={e.attack:.2f} [blue]D={e.defense:.2f}[/] "
                f"{bar(e.hp, e.max_hp)} [cyan]HP={e.hp:.2f}/{e.max_hp:.2f}\n"
            )
        else:
            sp = " " * 4
            console.print(
                f"[bold white]{e.name}[/]\n"
                f"{sp}[cyan]HP={e.hp:.2f}/{e.max_hp:.2f} {bar(e.hp, e.max_hp, 'green')}\n"
                f"{sp}[cyan]MP={e.mp:.2f}/{e.max_mp:.2f} {bar(e.mp, e.max_mp, 'blue')}\n"
                f"{sp}[red]A={e.attack:.2f} [blue]D={e.defense:.2f}\n"
                f"{sp}[bold red]S={e.strength} [bold blue]D={e.dexterity}"
                f" [bold yellow]W={e.wisdom} [bold green]E={e.endurance}"
                f" [bold white]F={e.free_points}[/]"
            )

    def presenses(self, entities: list[Entity]):
        console = self.game.console

        def bar(value, maximum, color="green", width=15):
            symlen = int(value / maximum * width) if maximum else 0
            return f"[white][[{color}]{'|'*symlen}{' '*(width-symlen)}[white]][/]"

        names = [e.name for e in entities]
        hps = [e.hp for e in entities]
        mhps = [e.max_hp for e in entities]
        atks = [e.attack for e in entities]
        defs = [e.defense for e in entities]
        nl = len(max(names, key=len))
        al = len(max(map(lambda x: f"{x:.2f}", atks), key=len))
        dl = len(max(map(lambda x: f"{x:.2f}", defs), key=len))
        hl = len(max(map(lambda x: f"{x:.2f}", hps), key=len))
        ml = len(max(map(lambda x: f"{x:.2f}", mhps), key=len))
        for e, n, h, mh, a, d in zip(entities, names, hps, mhps, atks, defs):
            text = f"[bold red]{e.strength}[bold blue]{e.dexterity}[bold yellow]{e.wisdom}[bold green]{e.endurance}"
            console.print(
                f"{text} [bold white]{n:<{nl}}[0 white]: [red]A={a:<{al}.2f} [blue]D={d:<{dl}.2f}[/] "
                f"{bar(h, mh)} [cyan]HP={h:<{hl}.2f} / {mh:<{ml}.2f}"
            )

    def __repr__(self):
        return "<Presenter>"
