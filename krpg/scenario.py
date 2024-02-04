from __future__ import annotations

import os
import zlib
from typing import Any, Optional, Self


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

    def __eq__(self, __value: object) -> bool:
        if isinstance(__value, Section):
            for i, j in zip(self.children, __value.children):
                if i != j:
                    return False
            for a, b in zip(self.args, __value.args):
                if a != b:
                    return False
            return self.name == __value.name
        return False


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

    def __repr__(self) -> str:
        """
        Returns a string representation of the Command object.

        Returns:
            str: The string representation of the Command object.
        """
        return f"Command({self.name!r}, args={self.args!r})"

    def __eq__(self, __value: object) -> bool:
        if isinstance(__value, Command):
            return self.name == __value.name and self.args == __value.args
        return False


def tokenize(text):
    text = text.strip()
    tokens = []
    temp = ""
    is_string = False
    is_comment = False
    close = None
    # TODO: Error handling
    # TODO: Add support for comments
    for i in text:
        if is_string and i != close:
            temp += i
            continue
        if is_comment:
            if i == "\n":
                is_comment = False
            else:
                continue

        if i in "{}":
            tokens.append(("BRACE", i))
        elif i in "\"'":
            is_string = not is_string
            close = i
            if not is_string:
                tokens.append(("QUOTED", temp))
                temp = ""
        elif i == "#":
            is_comment = not is_comment
        elif i == "\n":
            tokens.append(("TEXT", temp))
            tokens.append(("NEWLINE", "\n"))
            temp = ""
        elif i != " ":
            temp += i
        elif i == " " and temp:
            tokens.append(("TEXT", temp))
            temp = ""

    if temp:
        tokens.append(("TEXT", temp))
    return [
        [token[0].replace("QUOTED", "TEXT"), token[1]]
        for token in tokens
        if token[0] == "TEXT" and token[1] or token[0] != "TEXT"
    ]


class Block:
    def __init__(self, parrent=None) -> None:
        self.parrent: Block | None = parrent
        self.content: list[str] = []
        self.children: list[Block] = []

    def as_dict(self) -> dict[str, list]:
        dictionary: dict[str, list] = {
            "content": self.content,
        }
        if self.children:
            dictionary["children"] = [
                child.as_dict() for child in self.children if child
            ]
        return dictionary

    def __bool__(self):
        return bool(self.content or self.children)


def parse(tokens):
    result = Block()
    result.children.append(Block(result))
    current = result.children[0]
    for t, value in tokens:
        if t == "TEXT":
            current.content.append(value)
        elif t == "NEWLINE" and current.content:
            block = Block(current.parrent)
            if not current.parrent:
                raise Exception("Unexpected error")
            current.parrent.children.append(block)
            current = block
        elif t == "BRACE":
            if value == "{":
                block = Block(current)
                current.children.append(block)
                current = block
            elif value == "}":
                if not current.parrent:
                    raise Exception("Unexpected }")
                current = current.parrent
    return result.as_dict()["children"]


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
        def build_block(content, children, parrent=None) -> Section:
            block = Section(content[0], content[1:], parrent)
            for i in children:
                if "children" in i:
                    block.children.append(
                        build_block(i["content"], i["children"], block)
                    )
                else:
                    block.children.append(Command(i["content"][0], i["content"][1:]))
            return block

        return build_block([section_name], parse(text))

    def __repr__(self):
        return f"<Scenario {self.hash} c={len(self.children)}>"


# TODO: def merge(*sections) -> section
# sum(section.children for section in sections, [])
