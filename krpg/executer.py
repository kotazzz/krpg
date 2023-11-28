from __future__ import annotations

from typing import TYPE_CHECKING

from krpg.scenario import Command, Section, Multiline

if TYPE_CHECKING:
    from krpg.game import Game


def executer_command(name):
    """
    Decorator function that creates an instance of ExecuterCommand with the given name and callback function.

    Args:
        name (str): The name of the command.

    Returns:
        function: The wrapper function that creates an instance of ExecuterCommand.

    Example:
        @executer_command("my_command")
        def my_callback():
            pass
    """

    def wrapper(callback):
        return ExecuterCommand(name, callback)

    return wrapper


class ExecuterCommand:
    def __init__(self, name, callback):
        """
        Initializes an ExecuterCommand object.

        Args:
            name (str): The name of the command.
            callback (function): The callback function to be executed when the command is called.
        """
        self.name = name
        self.callback = callback


class Base:
    @executer_command("print")
    def builtin_print(game: Game, *args):
        text = " ".join(args)
        game.console.print("[blue]" + game.executer.process_text(text))

    @executer_command("$")
    def builtin_exec(game: Game, *code: list[str]):
        code = " ".join(code)
        env = game.executer.env | {"game": game, "env": game.executer.env}
        exec(code, env)

    @executer_command("set")
    def builtin_set(game: Game, name: str, expr: str):
        env = game.executer.env | {"game": game, "env": game.executer.env}
        game.executer.env[name] = eval(expr, env)

    @executer_command("if")
    def builtin_if(game: Game, expr: str, block: Block):
        env = game.executer.env | {"game": game, "env": game.executer.env}
        if eval(expr, env):
            block.run()


class Block:
    def __init__(self, executer: Executer, section: Section, parent=None):
        """
        Represents a block of code within the KRPG game.

        Args:
            executer (Executer): The executer object responsible for executing the code.
            section (Section): The section object containing the code.
            parent (Block, optional): The parent block of this block. Defaults to None.
        """
        self.pos = 0
        self.state = "stop"
        self.section = section
        self.code: list[Command | Section | Multiline] = section.children
        self.executer = executer
        self.execute = self.executer.create_execute([self])
        self.parent = parent

        @executer_command("print_block")  # TODO: Goto
        def print_block_command(game: Game):
            game.console.print(self)

        self.print_block_command = print_block_command

    def run(self, from_start: bool = True, *args, **kwargs):
        """
        Runs the block of code.

        Args:
            from_start (bool, optional): Indicates whether to start execution from the beginning of the block.
                Defaults to True.
        """
        if not self.code:
            return
        if from_start:
            self.pos = 0
        self.state = "run"
        while self.state == "run":
            pos = self.pos
            self.execute(self.code[self.pos])
            if pos == self.pos:  # if execute dont changed pos
                self.pos += 1
            if self.pos >= len(self.code):
                break
        self.state = "stop"


class Executer:
    """
    The Executer class is responsible for executing commands in the game.
    It manages extensions, commands, and the execution environment.

    Args:
        game (Game): The game instance.

    Attributes:
        game (Game): The game instance.
        extensions (list[object]): The list of extensions added to the executer.
        env (dict): The execution environment.
    """

    def __init__(self, game: Game):
        self.game = game
        self.extensions: list[object] = [Base()]
        self.env = {}
        game.add_saver("env", self.save, self.load)

    def save(self):
        """
        Save the execution environment.

        Returns:
            dict: The saved execution environment.
        """
        return {k: v for k, v in self.env.items() if not k.startswith("_")}

    def load(self, data):
        """
        Load the execution environment.

        Args:
            data (dict): The saved execution environment.
        """
        self.env = data

    def get_executer_additions(self, obj):
        """
        Get the executer additions from an object.

        Args:
            obj (object): The object to get the executer additions from.

        Returns:
            dict[str, ExecuterCommand]: The executer additions.
        """
        cmds: dict[str, ExecuterCommand] = {}
        for i in dir(obj):
            attr = getattr(obj, i)
            if isinstance(attr, ExecuterCommand):
                cmds[attr.name] = attr
        return cmds

    def add_extension(self, ext: object):
        """
        Add an extension to the executer.

        Args:
            ext (object): The extension to add.
        """
        self.game.log.debug(
            f"  [yellow3]Added ExecuterExtension [yellow]{ext.__class__.__name__}",
            stacklevel=2,
        )
        self.extensions.append(ext)

    def get_all_commands(self) -> dict[str, ExecuterCommand]:
        """
        Get all the commands from the extensions.

        Returns:
            dict[str, ExecuterCommand]: All the commands.
        """
        commands: dict[str, ExecuterCommand] = {}
        for ext in self.extensions:
            commands |= self.get_executer_additions(ext)
        return commands

    def create_execute(self, extensions: list[object]):
        """
        Create a new execute method that extends the extension list before running
        the command and returns it back after.

        Args:
            extensions (list[object]): The extensions to add temporarily.

        Returns:
            function: The new execute method.
        """

        def execute(command: Command):
            ext = self.extensions
            self.extensions += extensions
            self.execute(command)
            self.extensions = ext

        return execute

    def execute(self, command: Command | Section):
        """
        Execute a command by name, passing game, args, kwargs, and "block" kwarg if command has {}.

        Args:
            command (Command | Section): The command or section to execute.

        Raises:
            Exception: If the command is unknown.
        """
        commands = self.get_all_commands()
        if command.name in commands:
            self.game.log.debug(f"Executing {command.name} ")
            kwargs = {}
            if isinstance(command, Section):
                kwargs = {"block": self.create_block(command)}
            commands[command.name].callback(self.game, *command.args, **kwargs)
        else:
            raise Exception(f"Unknown command: {command.name}")

    def create_block(self, section: Section):
        """
        Create a block for a section.

        Args:
            section (Section): The section to create a block for.

        Returns:
            Block: The created block.
        """
        block = Block(self, section)
        return block

    def process_text(self, text: str):
        """
        Process the text by evaluating it in the execution environment.

        Args:
            text (str): The text to process.

        Returns:
            str: The processed text.
        """
        game = self.game
        env = game.executer.env | {"game": game, "env": game.executer.env}
        text = eval(f"f'''{text}'''", env)
        return text

    def __repr__(self):
        return (
            f"<Executer ext={len(self.extensions)} cmd={len(self.get_all_commands())}>"
        )
