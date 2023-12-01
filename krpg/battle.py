from __future__ import annotations

from typing import TYPE_CHECKING, Callable, cast
from krpg.entity import Entity
from krpg.events import Events

from krpg.executer import executer_command

if TYPE_CHECKING:
    from krpg.game import Game


class BattleManager:
    def __init__(self, game: Game):
        self.game = game
        self.game.executer.add_extension(self)

    def __repr__(self) -> str:
        return f"<BattleManager>"

    def predict(self, player: Entity, enemy: Entity) -> int:
        """
        Predicts the next action for the player in a battle based on the given player and enemy entities.

        Args:
            player (Entity): The player entity.
            enemy (Entity): The enemy entity.

        Returns:
            int: The predicted action for the player. 0 represents attack, 1 represents defend.
        """
        # Rule expressions:
        # player, enemy - Entity
        # actions: 0 - attack, 1 - defend
        # Rule format: ([...expressions (str)], action, weight)
        # [v] TODO: Lambda functions
        # rules = [
        #     # If enemy have 50%+ hp, then attack
        #     (["enemy.hp / enemy.max_hp >= 0.5"], 0, 1),
        #     # If enemy have 50%- hp, then defend
        #     (["enemy.hp / enemy.max_hp < 0.5"], 1, 1),
        #     # If player have 50%+ hp, then attack
        #     (["player.hp / player.max_hp >= 0.5"], 0, 0.5),
        #     # If player have 50%- hp, then attack
        #     (["player.hp / player.max_hp < 0.5"], 0, 1),
        # ]
        # results: list[tuple[int, int]] = []
        # env = {
        #     "player": player,
        #     "enemy": enemy,
        # }
        # for rule in rules:
        #     if all(eval(expr, env) for expr in rule[0]):
        #         results.append((rule[1], rule[2]))

        # [ ] TODO: int to IntEnum
        rules: list[tuple[Callable[[Entity, Entity], bool], int, float]] = [
            # If enemy have 50%+ hp, then attack
            (lambda player, enemy: enemy.hp / enemy.max_hp >= 0.5, 0, 1.0),
            # If enemy have 50%- hp, then defend
            (lambda player, enemy: enemy.hp / enemy.max_hp < 0.5, 1, 1.0),
            # If player have 50%+ hp, then attack
            (lambda player, enemy: player.hp / player.max_hp >= 0.5, 0, 0.5),
            # If player have 50%- hp, then attack
            (lambda player, enemy: player.hp / player.max_hp < 0.5, 0, 1.0),
        ]

        results = cast(
            list[tuple[int, float]],
            [(rule[1], rule[2]) for rule in rules if rule[0](player, enemy)],
        )

        assert results, Exception("No rules matched")
        chaos = 0.2  # random action chance and distance from best action

        # Select best action
        best_action = max(results, key=lambda x: x[1])[0]
        # Select random action
        random_action = self.game.random.choice([0, 1])  # [0, 1] - actions
        # TODO: replace best+random to weighted choice for all cases
        action = self.game.random.choices(
            [best_action, random_action], weights=[1 - chaos, chaos]
        )[0]
        return action

    @executer_command("fight_list")
    @staticmethod
    def command_fight_list(game: Game, *monster_ids: str):
        monster = game.random.choice(monster_ids)
        game.battle_manager.fight(monster)

    @executer_command("fight")
    @staticmethod
    def command_fight(game: Game, monster_id: str):
        game.battle_manager.fight(monster_id)

    def fight(self, monster_id: str):
        """
        Perform a battle between the player and a monster.

        Args:
            monster_id (str): The ID of the monster to fight.

        Returns:
            None
        """
        monster = self.game.bestiary.get_entity(monster_id)
        player = self.game.player
        console = self.game.console
        presenter = self.game.presenter
        console.print(f"Вы наткнулись на {monster.name}")
        spread = lambda s=5: self.game.random.randint(-s, s) / 100 + 1
        while True:
            presenter.presenses([player, monster])
            select: int = console.menu(
                2,
                [
                    ("Атаковать", 0),
                    ("Защититься", 1),
                    ("Сбежать", 2),
                ],
                view=lambda x: x[0],
            )[1]
            m_select = self.predict(player, monster)
            if select == 0:
                damage = player.attack * spread() - monster.defense * 0.1 * spread()
                if m_select == 1:
                    damage -= monster.defense * spread()
                damage = round(damage, 2)
                monster.hp -= damage
                console.print(
                    f"[green]Вы нанесли [red]{monster.name} [cyan]{damage} [green]урона"
                )
            if m_select == 0:
                damage = monster.attack * spread() - player.defense * 0.1 * spread()
                if select == 1:
                    damage -= player.defense * spread()
                damage = round(damage, 2)
                player.damage(damage)
                console.print(
                    f"[red]{monster.name} [green]нанес вам [cyan]{damage} [green]урона"
                )
            if select == 2:
                # chance 30% + 1/100 of player agility - 1/20 of monster agility
                chance = (
                    0.3
                    + player.attributes.agility / 100
                    - monster.attributes.agility / 20
                )
                if self.game.random.random() < chance:
                    console.print("[bold green]Вы убежали")
                    break
                else:
                    console.print("[bold yellow]Вы не смогли убежать")
            if player.hp <= 0:
                console.print("[bold red]Вы умерли!")
                break
            if monster.hp <= 0:
                console.print(f"[bold red]{monster.name} [bold green]умер!")
                money = int(monster.money * spread(15))
                player.add_money(money)
                console.print(
                    f"[bold green]Вы получили [cyan]{money} [bold green]монет"
                )
                self.game.events.dispatch(Events.KILL, monster_id=monster_id)
                break
