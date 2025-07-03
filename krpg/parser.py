from __future__ import annotations

from enum import Enum, auto

import attr


class TokenType(Enum):
    NEWLINE = auto()
    BRACE = auto()
    COMMAND = auto()


@attr.s(auto_attribs=True)
class Command:
    content: list[str] = attr.field(factory=lambda: [])
    parrent: Section = attr.field(default=None, repr=False)

    @property
    def name(self) -> str | None:
        return self.content[0] if self.content else None

    @property
    def args(self) -> list[str]:
        return self.content[1:]


@attr.s(auto_attribs=True)
class Section:
    content: list[str] = attr.field(factory=lambda: [])
    parrent: Section = attr.field(default=None, repr=False)
    children: list[Section | Command] = attr.field(factory=lambda: [])

    @property
    def name(self) -> str | None:
        return self.content[0] if self.content else None

    @property
    def args(self) -> list[str]:
        return self.content[1:]

    def add_children(self, item: Section | Command) -> None:
        item.parrent = self
        self.children.append(item)

    def get(self, name: str, command: bool = True, section: bool = True) -> Section | Command | None:
        for child in self.children:
            if child.name == name:
                if command or (section and isinstance(child, Section)):
                    return child
        return None

    def all(self, name: str = "", command: bool = True, section: bool = True) -> list[Section | Command]:
        result: list[Section | Command] = []
        for child in self.children:
            if not name or child.name == name:
                if command or (section and isinstance(child, Section)):
                    result.append(child)
        return result

    def has(self, name: str, command: bool = True, section: bool = True) -> bool:
        for child in self.children:
            if child.name == name:
                if command or (section and isinstance(child, Section)):
                    return True
        return False


def tokenize(text: str) -> list[tuple[TokenType, str]]:
    text = text.strip()
    tokens: list[tuple[TokenType, str]] = []
    temp = ""
    is_string = False
    is_comment = False
    close_char = None

    def add_temp(t: TokenType = TokenType.COMMAND) -> None:
        nonlocal temp
        if temp or is_string:
            tokens.append((t, temp.strip()))
            temp = ""

    for char in text:
        if is_string:
            if char == close_char:
                add_temp()
                is_string = False
            else:
                temp += char
            continue
        if is_comment:
            if char == "\n":
                is_comment = False
            else:
                continue
        if char in "{}":
            add_temp()
            tokens.append((TokenType.BRACE, char))
        elif char in "\"'`":
            is_string = True
            close_char = char
        elif char == "#":
            is_comment = True
        elif char == "\n":
            add_temp()
            tokens.append((TokenType.NEWLINE, "\n"))
        elif char != " ":
            temp += char
        else:
            add_temp()
    add_temp()
    tokens.append((TokenType.NEWLINE, "\n"))
    return tokens


def parse(tokens: list[tuple[TokenType, str]]) -> Section:
    result = Section()
    current: list[str] = []
    select = result

    for type, token in tokens:
        if type == TokenType.BRACE:
            if token == "{":
                new = Section(current)
                current = []
                select.add_children(new)
                select = new
            else:
                if current:
                    select.add_children(Command(current))
                    current = []
                select = select.parrent
        elif type == TokenType.COMMAND:
            current.append(token)
        elif type == TokenType.NEWLINE and current:
            select.add_children(Command(current))
            current = []
    return result


if __name__ == "__main__":
    # Пример использования
    text = """
    quests {
        quest command_help "Изучение команд" "Опробуйте некоторые команды" {
            stage 0 "Выполните команды" {
            goal run help "Команда помощи" "Вам нужно использовать команду [green]help[/] для получения помощи"
            goal run look "Команда осмотра" "Вам нужно использовать команду [green]look[/] для осмотра местности"
            goal run talk "Команда разговора" "Вам нужно использовать команду [green]talk[/] для разговора с людьми"
            reward end
            }
        }
    }
    """

    tokens = tokenize(text)

    from rich import print

    print(parse(tokens))
