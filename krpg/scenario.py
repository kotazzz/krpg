from __future__ import annotations
import shlex

ALLOW_KWARGS = True

class Section:
    def __init__(self, name, args=None, parent=None):
        self.name = name
        self.children: list[Section|Command]= []
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
    
    def all(self, name, section=True, command=True):
        r = []
        for child in self.children:
            if child.name == name:
                if isinstance(child, Section) and section:
                    return child
                if isinstance(child, Command) and command:
                    return child
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
                if arg.startswith('--'):
                    a, b = arg[2:].split('=')
                    args.pop(i)
                    kwargs[a] = b
        return Command(cmd, args, kwargs)
        

    def __repr__(self) -> str:
        return f"Command({self.name!r}, {self.args})"


def parse(text):
    text = text.replace("\n\n", "\n").replace("\\\n", '')
    lines = text.split("\n")
    lines = [r for line in lines if (r := line.split("#", 1)[0].strip())]
    curr = Section("root")
    for line in lines:
        if line == "}":
            curr = curr.parent
        elif line.endswith("{"):
            name, *args = shlex.split(line[:-1])
            new = Section(name, args, curr)
            curr.children.append(new)
            curr = new

        else:
            curr.children.append(Command.from_raw(line))
    return curr
