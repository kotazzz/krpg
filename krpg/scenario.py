from __future__ import annotations

import re
import shlex

ALLOW_KWARGS = True
MULOPEN = "[["
MULCLOSE = "]]"


class Section:
    def __init__(self, name, args=None, parent=None):
        self.name = name
        self.children: list[Section | Command] = []
        self.args = args or []
        self.parent = parent

    @property
    def as_command(self):
        return Command(self.name, self.args)

    def first(self, name, section=True, command=True):
        for child in self.children:
            if child.name == name:
                if isinstance(child, Section) and section:
                    return child
                if isinstance(child, Command) and command:
                    return child

    def all(self, name, section=True, command=True) -> list[Section | Command]:
        r = []
        for child in self.children:
            if child.name == name:
                if isinstance(child, Section) and section:
                    r.append(child)
                if isinstance(child, Command) and command:
                    r.append(child)
        return r

    def __repr__(self):
        return f"Section({self.name!r}, {self.args}, {self.children})"


class Command:
    def __init__(self, name, args=None, kwargs=None):
        self.name = name
        self.args = args or []
        self.kwargs = kwargs or {}

    @staticmethod
    def from_raw(string):
        cmd, *args = shlex.split(string)
        kwargs = {}
        if ALLOW_KWARGS:
            for i, arg in enumerate(args):
                if arg.startswith("--"):
                    a, b = arg[2:].split("=")
                    args.pop(i)
                    kwargs[a] = b
        return Command(cmd, args, kwargs)

    def __repr__(self) -> str:
        return f"Command({self.name!r}, {self.args})"


class Multiline(Command):
    def from_raw(string):
        return Multiline(string[len(MULOPEN) : -len(MULCLOSE)])

    def __repr__(self) -> str:
        return f"Multiline('{self.name[:10]+'...'}', {self.args})"


def parse(text):
    regex = re.escape(MULOPEN) + r'[^"|.]*' + re.escape(MULCLOSE)
    text = re.sub(regex, lambda m: m.group(0).strip().replace("\n", "\\n"), text)
    # print(text)
    text = text.replace("\n\n", "\n").replace("\\\n", "")

    lines = text.split("\n")

    lines = [r for line in lines if (r := line.split("#", 1)[0].strip())]
    current = Section("root")
    for line in lines:
        if line == "}":
            current = current.parent
        elif line.endswith("{"):
            name, *args = shlex.split(line[:-1])
            new = Section(name, args, current)
            current.children.append(new)
            current = new

        else:
            if line.startswith(MULOPEN):

                current.children.append(Multiline.from_raw(line))
            else:
                current.children.append(Command.from_raw(line))
    return current
