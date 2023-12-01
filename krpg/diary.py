from __future__ import annotations
from math import e

from typing import TYPE_CHECKING

from krpg.actions import action

if TYPE_CHECKING:
    from krpg.game import Game

    
    

# TODO: rewrite this
class DiaryManager:
    """
    Represents a diary in a game.

    Attributes:
    - records: A list of Record objects representing the diary entries.
    - game: A Game object representing the game the diary belongs to.

    Methods:
    - __init__(self, game: Game): Initializes a Diary object with the specified game.
    - save(self) -> dict: Saves the diary records as a dictionary.
    - load(self, data: dict): Loads the diary records from the given dictionary.
    - present(self, record: Record): Presents a formatted version of a diary record.
    - present_content(self, record: Record): Presents the content of a diary record.
    - action_diary(game: Game): Performs actions related to managing the diary.
    - __repr__(self) -> str: Returns a string representation of the Diary object.
    """

    def __init__(self, game: Game):
        self.game = game
        self.game.add_saver("diary", self.save, self.load)
        self.game.add_actions(self)

    def save(self):
        pass

    def load(self, data: dict):
        pass
    
    @action("diary", "Управление дневником", "Информация")
    @staticmethod
    def action_diary(game: Game):
        # v - view record
        # e - edit record
        # a - add record
        # d - delete record
        # l - list records
        # e - exit
        pass
        
    def __repr__(self) -> str:
        return f"<Diary>"
