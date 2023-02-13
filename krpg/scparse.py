from __future__ import annotations
import shlex
from dataclasses import dataclass, field


@dataclass
class Command:
    text: str

    @property
    def items(self):
        return shlex.split(self.text)

    @property
    def command(self):
        return self.items[0]

    @property
    def args(self):
        return self.items[1:]

    def __repr__(self):
        return f"Command({self.command!r})"

    def save(self):
        return self.text

    @classmethod
    def load(cls, data):
        return cls(data)


@dataclass
class Section:
    head: Command
    body: list[Section | Command] = field(default_factory=list)

    def save(self):
        data = [self.head.text, [x.save() for x in self.body]]
        return data

    @classmethod
    def load(cls, data):
        head, body = data
        return cls(
            Command(head),
            [
                Command.load(x) if isinstance(x, bytes) else Section.load(x)
                for x in body
            ],
        )

    def __post_init__(self):
        if isinstance(self.head, str):
            self.head = Command(self.head)

    def get_items(self, name):
        for item in self.body:
            if isinstance(item, Section):
                if item.head.command == name:
                    yield item
            elif isinstance(item, Command):
                if item.command == name:
                    yield item

    @property
    def sections(self):
        return [x for x in self.body if isinstance(x, Section)]

    @property
    def commands(self):
        return [x for x in self.body if isinstance(x, Command)]

    def __getattribute__(self, __name: str):
        if __name in ("head", "body", "sections", "commands", "get_items", "save", "load", "__post_init__"):
            return super().__getattribute__(__name)
        else:
            return list(self.get_items(__name))


def parse(text):
    text = text.replace("\\\n", "").splitlines()
    text = [x for x in map(str.strip, text) if x and not x.startswith("#")]
    data = Section("root")
    stack = [data]
    for line in text:
        if line.startswith("@"):
            if line == "@!":
                stack.pop()
            else:
                s = Section(line[1:])
                stack[-1].body.append(s)
                stack.append(s)
        else:
            stack[-1].body.append(Command(line))
    return data


def build(data, indent=0):
    text = ""
    for item in data.body:
        if isinstance(item, Command):
            text += " " * (indent * 4) + item.text + "\n"
        else:
            text += " " * (indent * 4) + "@" + item.head.text + "\n"
            text += build(item, indent + 1)
            text += " " * (indent * 4) + "@!\n\n"
    return text
