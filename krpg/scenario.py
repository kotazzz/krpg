from __future__ import annotations

import os
import re
import shlex
import zlib
from typing import Any, Optional, Self

ALLOW_KWARGS = True
MULOPEN = "<|"
MULCLOSE = "|>"


class UnexpectedEnd(Exception):
    pass


class Section:
    """
    Represents a section in a scenario.

    Attributes:
        name (str): The name of the section.
        args (list, optional): The arguments of the section. Defaults to an empty list.
        parent (Section, optional): The parent section of the current section. Defaults to None.
        children (list[Section | Command]): The children sections or commands of the current section.
    """

    def __init__(
        self,
        name: str,
        args: Optional[list[str]] = None,
        parent: Optional[Section] = None,
    ):
        self.name = name
        self.children: list[Section | Command] = []
        self.args = args or []
        self.parent = parent

    @property
    def as_command(self):
        """Return section as command"""
        return Command(self.name, self.args)

    def first(self, *a, **k) -> None:
        """
        Returns the first child section or command with the specified name.

        Args:
            name (str): The name of the child section or command.
            section (bool, optional): Whether to consider child sections. Defaults to True.
            command (bool, optional): Whether to consider child commands. Defaults to True.

        Returns:
            Section | Command | None: The first child section or command with the specified name, or None if not found.
        """
        raise DeprecationWarning("Use first_command or first_section instead")
        # TODO: remove this method
        # for child in self.children:
        #     if child.name == name:
        #         if isinstance(child, Section) and section:
        #             return child
        #         if isinstance(child, Command) and command:
        #             return child
        # return None

    def first_command(self, name: str) -> Command:
        """
        Returns the first child command with the specified name.

        Args:
            name (str): The name of the child command.

        Returns:
            Command: The first child command with the specified name.

        Raises:
            ValueError: If the command with the specified name is not found.
        """
        for child in self.children:
            if child.name == name and isinstance(child, Command):
                return child
        raise ValueError(f"Command {name} not found")

    def has_command(self, name: str) -> bool:
        """
        Returns whether the section has a child command with the specified name.

        Args:
            name (str): The name of the child command.

        Returns:
            bool: Whether the section has a child command with the specified name.
        """
        for child in self.children:
            if child.name == name and isinstance(child, Command):
                return True
        return False

    def first_section(self, name: str) -> Section:
        """Returns the first child section with the specified name.

        Parameters
        ----------
        name : str
            The name of the child section.

        Returns
        -------
        Section
            The first child section with the specified name.

        Raises
        ------
        ValueError
            If the section with the specified name is not found.
        """
        for child in self.children:
            if child.name == name and isinstance(child, Section):
                return child
        raise ValueError(f"Section {name} not found")

    def has_section(self, name: str) -> bool:
        """
        Returns whether the section has a child section with the specified name.

        Args:
            name (str): The name of the child section.

        Returns:
            bool: Whether the section has a child section with the specified name.
        """
        for child in self.children:
            if child.name == name and isinstance(child, Section):
                return True
        return False

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
        r: list[Section | Command] = []
        for child in self.children:
            if child.name == name:
                if isinstance(child, Section) and section:
                    r.append(child)
                if isinstance(child, Command) and command:
                    r.append(child)
        return r

    def all_commands(self, name: str = "") -> list[Command]:
        """
        Returns a list of all child commands with the specified name.
        If the name is empty, returns all child commands.

        Args:
            name (str): The name of the child commands.

        Returns:
            list[Command]: A list of all child commands with the specified name.
        """
        r: list[Command] = []
        for child in self.children:
            if (not name or child.name == name) and isinstance(child, Command):
                r.append(child)
        return r

    def all_sections(self, name: str = "") -> list[Section]:
        """
        Returns a list of all child sections with the specified name.

        Args:
            name (str): The name of the child sections.

        Returns:
            list[Section]: A list of all child sections with the specified name.
        """
        r: list[Section] = []
        for child in self.children:
            if (not name or child.name == name) and isinstance(child, Section):
                r.append(child)
        return r

    def join(self, section: Section, inner_merge: bool = False) -> None:
        """
        Joins the children of the current section with the children of the specified section.
        Args:
            section (Section): The section whose children will be joined with the current section's children.
            inner_merge (bool, optional): Whether to perform inner merge for sections with the same name. Defaults to False.
        """
        if inner_merge:
            for child in section.children:
                if isinstance(child, Section):
                    if self.has_section(child.name):
                        existing_section = self.first_section(child.name)
                        existing_section.join(child, inner_merge=True)
                    else:
                        self.children.append(child)
                else:
                    self.children.append(child)
        else:
            self.children.extend(section.children)

    def __repr__(self):
        return f"Section({self.name!r}, args={self.args!r}, children={self.children!r})"

    def __rich_repr__(self):
        yield self.name
        yield self.args
        yield self.children


class Command:
    def __init__(
        self,
        name,
        args: Optional[list[str]] = None,
        kwargs: Optional[dict[str, Any]] = None,
    ):
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
        return f"Command({self.name!r}, args={self.args!r})"


class Multiline(Command):
    @staticmethod
    def from_raw(string) -> Multiline:
        return Multiline(string[len(MULOPEN) : -len(MULCLOSE)])  # noqa

    def __repr__(self) -> str:
        return f"Multiline('{self.name[:10]+'...'}', {self.args})"

    def __rich_repr__(self):
        yield self.name
        yield self.args


class Scenario(Section):
    """
    Represents a scenario in the game.

    Attributes:
        hash (str): The hash value of the scenario file.
        name (str): The name of the section.
        args (list, optional): The arguments of the section. Defaults to an empty list.
        parent (Section, optional): The parent section of the current section. Defaults to None.
        children (list): The list of child sections in the scenario.

    Methods:
        parse(str): Parses given content and appends children to the current section.
    """

    def __init__(self) -> None:
        super().__init__("root")
        self.hash: dict[str, str] = {}

    def add_section(self, path: str, base_path: Optional[str] = None) -> Self:
        """
        Adds a section from a scenario file.

        Args:
            path (str): The path to the scenario file.
            base_path (str, optional): The base path to the scenario file. Defaults to None.

        Returns:
            Self: The Scenario object.
        """
        with open(path, "r", encoding="utf-8") as f:
            text = f.read()
        section = self.parse(text, path)
        if base_path:
            filename = os.path.relpath(path, base_path)
        else:
            filename = path
        self.hash[filename] = f"{zlib.crc32(text.encode('utf-8')):x}"
        self.join(section, True)
        return self  # for chaining

    def parse(self, text: str, section_name: str = "root") -> Section:
        """
        Parses given content and appends children to the current section.
        """
        regex = re.escape(MULOPEN) + r'[^"|.]*' + re.escape(MULCLOSE)
        text = re.sub(regex, lambda m: m.group(0).strip().replace("\n", "\\n"), text)
        text = text.replace("\n\n", "\n").replace("\\\n", "")
        lines = [r for line in text.split("\n") if (r := line.split("#", 1)[0].strip())]
        current = Section(section_name)
        for line in lines:
            if line == "}":
                if not current.parent:
                    raise UnexpectedEnd("Unexpected }")
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
