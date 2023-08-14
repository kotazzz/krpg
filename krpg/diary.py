
from __future__ import annotations
from math import e

from typing import TYPE_CHECKING

from krpg.actions import action
if TYPE_CHECKING:
    from krpg.game import Game

class Record:
    def __init__(self, day: int, text: str):
        self.day = day
        self.text = text
class Diary:
    def __init__(self, game: Game):
        self.records: list[Record] = [] # (Day #, text)
        self.game = game
        self.game.add_saver("diary", self.save, self.load)
        self.game.add_actions(self)
    def save(self) -> dict:
        return [(record.day, record.text) for record in self.records]
    def load(self, data: dict):
        self.records = [Record(*record) for record in data]
    def present(self, record:Record):
        text = record.text.replace("\n", " ")
        text =  text[:10] + '...' if len(text) > 10 else text
        return f"[green]День {record.day}[/] - {text}"
    def present_content(self, record: Record):
        console = self.game.console
        console.print(f"[bold green]Запись дня {record.day}[/]")
        lines = record.text.split("\n")
        for i, line in enumerate(lines):
            console.print(f"  [green]{i}[white]) {line}")
        return lines 
    @action("diary", "Управление дневником", "Информация")
    def action_diary(game: Game):
        # v - view record
        # e - edit record
        # a - add record
        # d - delete record
        # l - list records
        # e - exit
        console = game.console
        while True:
            for i, rec in enumerate(game.diary.records):
                console.print(f" [cyan]{i}[white]) {game.diary.present(rec)}")    
            res = console.prompt("[green]Выберите действие: ", {
                "a": "Добавить запись",
                "e": "Выход",
                **{str(i): game.diary.present(rec) for i, rec in enumerate(game.diary.records)},
            },)
            if res == "a":
                day = game.clock.days
                text = console.prompt("[green]Введите текст записи: ")
                game.diary.records.append(Record(day, text))
            elif res == "e":
                break
            elif res.isdigit():
                game.diary.present_content(game.diary.records[int(res)])
                op = console.prompt("[green]Выберите действие: ", {
                    "e": "Редактировать строку",
                    "a": "Добавить строку",
                    "d": "Удалить запись",
                    "q": "Отмена",
                })
                if op == "q":
                    continue
                elif op == "e":
                    linenum = console.prompt("[green]Введите номер строки: ")
                    if not linenum.isdigit() or int(linenum) >= len(game.diary.records[int(res)].text.split("\n")):
                        continue
                    line = console.prompt("[green]Введите текст строки: ")
                    if line == "e":
                        continue
                    text = game.diary.records[int(res)].text.split("\n")
                    if line == "":
                        text.pop(int(linenum))
                    else:
                        text[int(linenum)] = line
                    game.diary.records[int(res)].text = "\n".join(text)
                    
                elif op == "a":
                    text = console.prompt("[green]Введите текст строки: ")
                    game.diary.records[int(res)].text += "\n" + text
                elif op == "d":
                    game.diary.records.pop(int(res))
            else:
                console.print("[red]Неверная команда")
    def __repr__(self) -> str:
        return f"<Diary rec={len(self.records)}>"    
                    
                
                
                    
                    
                    
            