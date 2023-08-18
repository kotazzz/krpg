
from krpg.actions import action
from typing import TYPE_CHECKING

from krpg.executer import executer_command

if TYPE_CHECKING:
    from krpg.game import Game


"""
quests {
  quest first_meet "Первая встреча" "Ваше приключение только начинается" {
      
  }
}
"""

class Quest:
    def __init__(self, id, name, description, goals, rewards):
        self.id = id
        self.name = name
        self.description = description
        self.goals = goals
        self.rewards = rewards
    

class QuestState:
    def __init__(self, quest: Quest, state):
        self.quest = quest
        self.state = state
        
class QuestManager:
    def __init__(self, game: "Game"):
        self.game = game
        self.quests = []
        self.actions = []
        self.game.executer.add_extension(self)
        self.game.add_saver("quest", self.save, self.load)

    def load(self):
        pass

    def save(self):
        pass

    def __repr__(self):
        return f"<QuestManager q={len(self.quests)}>"

