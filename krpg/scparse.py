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

    def get_section(self, name):
        for item in self.body:
            if isinstance(item, Section) and item.head.command == name:
                return item

    def get_sections(self, name):
        for item in self.body:
            if isinstance(item, Section) and item.head.command == name:
                yield item

    def get_command(self, name):
        for item in self.body:
            if isinstance(item, Command) and item.command == name:
                return item

    def get_commands(self, name):
        for item in self.body:
            if isinstance(item, Command) and item.command == name:
                yield item

    def get_items(self, name):
        for item in self.body:
            if isinstance(item, (Section, Command)):
                yield item

    def get_all_commands(self):
        for item in self.body:
            if isinstance(item, Command):
                yield item

    def get_all_sections(self):
        for item in self.body:
            if isinstance(item, Section):
                yield item

    def __getitem__(self, key) -> list[Section | Command] | Section | Command:
        if isinstance(key, slice):
            # 1 - name
            # 2 - one, all (default)
            # 3 - commands, sections, all (default)
            name, mode, type = key.start, key.stop or "all", key.step or "all"
            if name:
                funcs = {
                    ("command", "one"): self.get_command,
                    ("command", "all"): lambda x: list(self.get_commands(x)),
                    ("section", "one"): self.get_section,
                    ("section", "all"): lambda x: list(self.get_sections(x)),
                    ("all", "one"): lambda x: self.get_items(x)[0],
                    ("all", "all"): lambda x: list(self.get_items(x)),
                }
                return funcs[type, mode](name)
            else:
                # return all
                funcs = {
                    "command": lambda: self.get_all_commands(),
                    "section": lambda: self.get_all_sections(),
                    "all": lambda: self.get_items(),
                }
                return list(funcs[type]())

        return list(self.get_items(key))


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
