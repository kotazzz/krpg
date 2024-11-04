from __future__ import annotations
from krpg.parser import parse, tokenize
from typing import TYPE_CHECKING
import os

if TYPE_CHECKING:
    from krpg.game import Game

MAIN_FILE = "main.krpg"

BASE_FOLDER = "content"


class Builder:
    def __init__(self, game: Game):
        self.game = game

    def build(self):
        if __package__ is None:
            raise ValueError("Package is not set")
        with open(
            f"{os.path.abspath(__package__)}/{BASE_FOLDER}/{MAIN_FILE}", "r"
        ) as file:
            self.main = parse(tokenize(file.read()))

        init = self.main.get("init")
        if not init:
            raise ValueError("No init section found")
        self.game.executer.run(init)
