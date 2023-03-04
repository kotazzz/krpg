from __future__ import annotations
import random

import shlex
import time
from typing import Iterable

from prompt_toolkit.application import Application
from prompt_toolkit.buffer import Buffer
from prompt_toolkit.completion import CompleteEvent, Completion, WordCompleter
from prompt_toolkit.document import Document
from prompt_toolkit.formatted_text import ANSI
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.key_binding.key_processor import KeyPressEvent
from prompt_toolkit.layout import CompletionsMenu, Float, FloatContainer, ScrollablePane
from prompt_toolkit.layout.containers import HSplit, Window, to_container
from prompt_toolkit.layout.layout import Layout
from prompt_toolkit.widgets import Frame, Label, TextArea
from rich.console import Console
from prompt_toolkit.layout.screen import WritePosition


class InterfaceCommand:
    def __init__(self, name, description):
        self.name = name
        self.description = description


class DynamicWordCompleter(WordCompleter):
    def __init__(self, callback):
        self.callback = callback
        super().__init__([])

    def get_completions(
        self, document: Document, complete_event: CompleteEvent
    ) -> Iterable[Completion]:
        self.words = self.callback()
        return super().get_completions(document, complete_event)


class Interface:
    def __init__(self):
        self.cmd_info = Label("Hello, world!")
        self.text_area = TextArea(
            text=f"",
            prompt="> ",
            completer=DynamicWordCompleter(self.generate_completer),
        )
        self.commands: list[InterfaceCommand] = []
        self.set_commands(
            InterfaceCommand("test", "test command"),
            InterfaceCommand("help", "help command"),
            InterfaceCommand("exit", "exit command"),
        )

        self.text_area.buffer.on_text_changed.add_handler(self.on_text_changed)

        self.pane = ScrollablePane(HSplit([]))
        self.hidden = []
        self.index = 0
        self.kb = KeyBindings()
        self.kb.add("enter")(self.handle_input)
        self.kb.add("c-c")(self.exit_)
        self.kb.add("down")(self.down)
        self.kb.add("up")(self.up)
        self.console = Console(highlight=False)
        self.allow_delay = True
        root = HSplit(
            [
                Frame(self.pane),
                self.cmd_info,
                Frame(self.text_area, height=5),
            ],
        )

        root = FloatContainer(
            root,
            floats=[
                Float(
                    xcursor=True,
                    ycursor=True,
                    content=CompletionsMenu(max_height=5, scroll_offset=1),
                ),
            ],
        )

        self.root = Layout(container=root)
        self.app = Application(
            layout=self.root, key_bindings=self.kb, full_screen=True, mouse_support=True
        )
        self.app.run()

    def exit_app(self):
        self.app.exit()

    def set_commands(self, *cmds):
        self.commands.clear()
        self.commands.extend(cmds)

    def on_text_changed(self, b: Buffer):
        t = shlex.split(b.text)
        if not t:
            return
        self.cmd_info.text = "Unknown command"
        for cmd in self.commands:
            if cmd.name == t[-1]:
                self.cmd_info.text = cmd.description

    def generate_completer(self):
        return [cmd.name for cmd in self.commands]

    def add_label(self, label: Label):
        panel: HSplit = self.pane.get_children()[0]
        label = Label(ANSI(label.text))
        panel.children.append(to_container(label))

    def edit(self, label: Label):
        panel: HSplit = self.pane.get_children()[0]
        label = Label(ANSI(label.text))
        panel.children[-1] = to_container(label)

    def print(
        self,
        *text,
        end="",
        sep=",",
        min=0,
        max=None,
        format=True,
        convert_float=True,
        line_delay=True,
    ):

        # self.add_label(Label(self.format(f"[red]{text}[/]")))
        # self.edit(Label(self.format(f"[red]{text}[/]!")))

        self.add_label(Label("1"))

        content = ""

        def add(string):
            nonlocal content
            content += string
            self.edit(Label(content))

        min = min if self.allow_delay else 0
        text = [
            f"{i:.2f}" if convert_float and isinstance(i, float) else str(i)
            for i in text
        ]
        if format:
            text = [self.format(str(i)) for i in text]

        if min != 0:
            text = sep.join(text) + end
            text = text.splitlines()
            for line in text:
                for i in line:
                    delay = random.uniform(min, max or min)
                    add(i)
                    time.sleep(delay)
                    # self.app.renderer

                    #!!!!!!!!!!!!
                    from prompt_toolkit.layout.mouse_handlers import MouseHandlers
                    from prompt_toolkit.layout.screen import Char, Screen

                    output = self.app.renderer.output
                    screen = Screen()
                    mouse_handlers = MouseHandlers()
                    size = output.get_size()

                    if self.app.renderer.full_screen:
                        height = size.rows
                    self.pane.write_to_screen(
                        screen,
                        mouse_handlers,
                        WritePosition(
                            xpos=0, ypos=0, width=size.columns, height=height
                        ),
                        parent_style="",
                        erase_bg=False,
                        z_index=None,
                    )
                    #!!!!!!!!!!!!

                time.sleep(delay * 30 * line_delay)
                add("\n")
        else:
            text = sep.join(text) + end
            add(text)

    def handle_input(self, event: KeyPressEvent):
        text = self.text_area.buffer.text
        self.text_area.buffer.text = ""

        self.print(f"[red]{text}[/]")
        self.print(
            "[bold magenta]╭───╮ ╭─╮[bold red]       [bold blue]╭──────╮  [bold yellow]╭───────╮[bold green]╭───────╮\n"
            "[bold magenta]│   │ │ │[bold red]       [bold blue]│   ╭─╮│  [bold yellow]│       │[bold green]│       │\n"
            "[bold magenta]│   ╰─╯ │[bold red]╭────╮ [bold blue]│   │ ││  [bold yellow]│   ╭─╮ │[bold green]│   ╭───╯\n"
            "[bold magenta]│     ╭─╯[bold red]╰────╯ [bold blue]│   ╰─╯╰─╮[bold yellow]│   ╰─╯ │[bold green]│   │╭──╮\n"
            "[bold magenta]│     ╰─╮[bold red]       [bold blue]│   ╭──╮ │[bold yellow]│   ╭───╯[bold green]│   ││  │\n"
            "[bold magenta]│   ╭─╮ │[bold red]       [bold blue]│   │  │ │[bold yellow]│   │    [bold green]│   ╰╯  │\n"
            "[bold magenta]╰───╯ ╰─╯[bold red]       [bold blue]╰───╯  ╰─╯[bold yellow]╰───╯    [bold green]╰───────╯\n[/]",
            min=0.00001,
        )

        self.scroll(self.get_lines())

    def format(self, text):
        with self.console.capture() as cap:
            self.console.print(text, end="")
        return cap.get()

    def get_lines(self):
        panel: HSplit = self.pane.get_children()[0]
        windows: Window = panel.get_children()
        norm = lambda x: x.value if isinstance(x, ANSI) else x
        lines = sum(
            [len(norm(window.content.text()).split("\n")) for window in windows]
        )
        return lines

    def scroll(self, amount):
        # print(len(panel.get_children()))
        lines = self.get_lines()
        self.pane.vertical_scroll = min(
            lines - 30, max(0, self.pane.vertical_scroll + amount)
        )

    def down(self, event):
        self.scroll(1)

    def up(self, event):
        self.scroll(-1)

    def exit_(self, event: KeyPressEvent):
        self.app.exit()


Interface()
