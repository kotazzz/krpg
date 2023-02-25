from __future__ import annotations
import random

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .game import Game

from .executer import ExecuterExtension, executer_command


class BattleManager(ExecuterExtension):
    def __init__(self, game: Game):
        self.game = game
        self.game.executer.add_extension(self)

    @executer_command(name="battle")
    def battle(game: Game, identifier):
        player = game.player.entity
        c = game.console

        game.logger.debug(f"Fight with {identifier}")
        entity = game.bestiary.get_entity(identifier)
        c.print(f"[bold red]Вы встретили {entity.name}[/]")
        game.presenter.presense(entity)
        c.print("Выбор действия:")
        c.print("[red] 1 [/] Атака")
        c.print("[blue] 2 [/] Защита")
        c.print("[yellow] 3 [/] Попытка побега (40%)")

        while True:
            pselect = c.number_menu(2, 3) + 1
            eselect = random.choices(range(1, 3), [0.6, 0.4], k=1)[0]
            messages = {
                1: "[cyan]{a}[yellow] наносит [green]{d:.2f}[yellow] урона [cyan]{b}[/]",
                2: "[cyan]{a}[yellow] защищается и поглощает [green]{d:.2f}[yellow] урона[/]",
                3: "[cyan]{a}[yellow] пытается сбежать[/]",
            }
            if pselect == 3:
                if random.random() < 0.4:
                    game.eh.dispatch("escape", entity=entity)
                    c.print("[green]Вы успешно сбежали![/]")
                else:
                    c.print("[red]Сбежать не удалось![/]")

            player_def = player.defense * (pselect == 2)
            enemy_def = -entity.defense * (eselect == 2)
            player_damage = entity.attack * (eselect == 1) - player_def
            player_damage += player_damage * random.random() - 0.5 / 10
            entity_damage = player.attack * (pselect == 1) - enemy_def
            entity_damage += entity_damage * random.random() - 0.5 / 10

            ab = {
                "a": player.name,
                "b": entity.name,
                "d": player_damage if pselect == 1 else player_def,
            }
            ba = {
                "a": entity.name,
                "b": player.name,
                "d": entity_damage if eselect == 1 else enemy_def,
            }

            player.damage(player_damage)
            entity.damage(entity_damage)

            c.print(messages[pselect].format(**ab))
            c.print(messages[eselect].format(**ba))
            game.presenter.presenses([player, entity])

            if player.hp == 0:
                game.console.print(f"[red]Вы погибли")
                game.eh.dispatch(f"player_death")
                break
            elif entity.hp == 0:
                game.console.print(f"[red]Вы победили!")
                game.eh.dispatch(f"player_kill", entity=entity)
                break

    def __repr__(self):
        return "<BattleManager>"
