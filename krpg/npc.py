from __future__ import annotations
from krpg.actions import Action, action
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from krpg.game import Game


class Npc:
    def __init__(self, id: str, name: str, description: str, state: str,
                 location: str, actions: dict[str, list[Action]]
                 ):
        self.id: str = id
        self.name: str = name
        self.state: str = state
        self.description: str = description
        self.location: str = location
        self.actions: dict[str, list[Action]] = actions # {state: [actions]}
    def get_actions(self):
        return self.actions[self.state]
    
    def __repr__(self) -> str:
        return f"<Npc name={self.name!r} state={self.state!r}>"
    
class NpcManager:
    def __init__(self, game: Game):
        self.game = game
        self.npcs: list[Npc] = []
        self.game.add_saver("npcs", self.save, self.load)
        self.game.add_actions(self)
    
    def save(self):
        pass
    def load(self, data):
        pass
    def get_npcs(self, location: str):
        return [npc for npc in self.npcs if npc.location == location]
    
    @action("talk", "Поговорить с доступными нпс", "Действия")
    def action_talk(game:Game):
        loc = game.world.current
        npcs = game.npc_manager.get_npcs(loc.id)
        sel: Npc = game.console.menu(2, npcs, "e", lambda n: n.name, title="Выберите нпс")
        if not sel:
            return
        sel_act: Action = game.console.menu(2, sel.get_actions(), "e", lambda a: a.description, title="Выберите действие")
        if not sel_act:
            return 
        sel_act.callback(game)