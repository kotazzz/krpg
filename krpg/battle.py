
from __future__ import annotations

from typing import TYPE_CHECKING
from krpg.entity import Entity

from krpg.executer import executer_command

if TYPE_CHECKING:
    from krpg.game import Game




class BattleManager:
    def __init__(self, game: Game):
        self.game = game
        
    def __repr__(self) -> str:
        return f"<BattleManager>"
    
    def predict(self, player: Entity, enemy: Entity):
        rules = [
            player.hp 
        ]
    
    @executer_command("fight")
    def fight(game: Game, monster_id: str):
        monster = game.bestiary.get_entity(monster_id)
        player = game.player
        console = game.console
        presenter = game.presenter
        console.print(f"Вы наткнулись на {monster.name}")
        while True:
            presenter.presenses([player, monster])
            select = console.menu(2, [
                ("Атаковать", 0),
                ("Защититься", 1),
                ("Сбежать", 2),
            ], view=lambda x: x[0])
            m_select = 0