from __future__ import annotations

import re
import shlex
import zlib

ALLOW_KWARGS = True
MULOPEN = "[["
MULCLOSE = "]]"


class Section:
    """
    Represents a section in a scenario.

    Attributes:
        name (str): The name of the section.
        args (list, optional): The arguments of the section. Defaults to an empty list.
        parent (Section, optional): The parent section of the current section. Defaults to None.
        children (list[Section | Command]): The children sections or commands of the current section.
    """

    def __init__(self, name, args=None, parent=None):
        self.name = name
        self.children: list[Section | Command] = []
        self.args = args or []
        self.parent = parent

    @property
    def as_command(self):
        return Command(self.name, self.args)

    def first(self, name, section=True, command=True) -> Section | Command | None:
        """
        Returns the first child section or command with the specified name.

        Args:
            name (str): The name of the child section or command.
            section (bool, optional): Whether to consider child sections. Defaults to True.
            command (bool, optional): Whether to consider child commands. Defaults to True.

        Returns:
            Section | Command | None: The first child section or command with the specified name, or None if not found.
        """
        for child in self.children:
            if child.name == name:
                if isinstance(child, Section) and section:
                    return child
                if isinstance(child, Command) and command:
                    return child

    def all(self, name, section=True, command=True) -> list[Section | Command]:
        """
        Returns a list of all child sections or commands with the specified name.

        Args:
            name (str): The name of the child sections or commands.
            section (bool, optional): Whether to consider child sections. Defaults to True.
            command (bool, optional): Whether to consider child commands. Defaults to True.

        Returns:
            list[Section | Command]: A list of all child sections or commands with the specified name.
        """
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
        """
        Initializes a Command object.

        Args:
            name (str): The name of the command.
            args (list, optional): The arguments of the command. Defaults to None.
            kwargs (dict, optional): The keyword arguments of the command. Defaults to None.
        """
        self.name = name
        self.args = args or []
        self.kwargs = kwargs or {}

    @staticmethod
    def from_raw(string):
        """
        Creates a Command object from a raw string.

        Args:
            string (str): The raw string representing the command.

        Returns:
            Command: The created Command object.
        """
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
        """
        Returns a string representation of the Command object.

        Returns:
            str: The string representation of the Command object.
        """
        return f"Command({self.name!r}, {self.args})"


class Multiline(Command):
    def from_raw(string):
        return Multiline(string[len(MULOPEN) : -len(MULCLOSE)])

    def __repr__(self) -> str:
        return f"Multiline('{self.name[:10]+'...'}', {self.args})"


class Scenario(Section):
    """
    Represents a scenario in the game.

    Args:
        file (str): The path to the scenario file.

    Attributes:
        file (str): The path to the scenario file.
        hash (str): The hash value of the scenario file.
        children (list): The list of child sections in the scenario.

    Methods:
        parse(): Parses the scenario file and builds the section hierarchy.
    """

    def __init__(self, file):
        super().__init__("root")
        self.file = file
        self.hash = f"{zlib.crc32(open(file, 'rb').read()):x}"
        self.parse()

    def parse(self):
        """
        Parses the scenario file and builds the section hierarchy.
        """
        text = open(self.file, encoding="utf-8").read()
        regex = re.escape(MULOPEN) + r'[^"|.]*' + re.escape(MULCLOSE)
        text = re.sub(regex, lambda m: m.group(0).strip().replace("\n", "\\n"), text)
        text = text.replace("\n\n", "\n").replace("\\\n", "")
        lines = text.split("\n")
        lines = [r for line in lines if (r := line.split("#", 1)[0].strip())]
        current = self
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

    def __repr__(self):
        return f"<Scenario {self.hash} c={len(self.children)}>"


# TODO: def merge(*sections) -> section
# sum(section.children for section in sections, [])
