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


@dataclass
class Section:
    head: Command
    body: list[Section | Command] = field(default_factory=list)

    def __post_init__(self):
        if isinstance(self.head, str):
            self.head = Command(self.head)

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
    return data.body