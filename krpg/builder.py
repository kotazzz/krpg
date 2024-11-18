from __future__ import annotations
from krpg.parser import Section, parse, tokenize
from typing import TYPE_CHECKING
import os


if TYPE_CHECKING:
    from krpg.game import Game

MAIN_FILE = "main.krpg"

BASE_FOLDER = "content"


def build_scenarios(game: Game, section: Section) -> None:
    for scenario in section.all(command=False):
        assert isinstance(scenario, Section)
        game.bestiary.add(
            game.executer.create_scenario(scenario),
        )


def build_items(game: Game, section: Section) -> None:
    pass


def build_npcs(game: Game, section: Section) -> None:
    pass


def build_locations(game: Game, section: Section) -> None:
    pass


def build_quests(game: Game, section: Section) -> None:
    pass


class Builder:
    def __init__(self, game: Game):
        self.game = game

    def build(self) -> None:
        if __package__ is None:
            raise ValueError("Package is not set")
        path = f"{os.path.abspath(__package__)}/{BASE_FOLDER}/{MAIN_FILE}"
        with open(path, "r", encoding="utf-8") as file:
            self.main = parse(tokenize(file.read()))

        steps = [
            ("scenarios", build_scenarios),
            ("items", build_items),
            ("npcs", build_npcs),
            ("locations", build_locations),
            ("quests", build_quests),
        ]
        for name, step in steps:
            section = self.main.get(name)
            if section:
                assert isinstance(section, Section)
                step(self.game, section)

        init = self.main.get("init")
        if not init:
            raise ValueError("No init section found")
        assert isinstance(init, Section)
        self.game.executer.run(init)
