from __future__ import annotations
import shlex
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.application import Application
from prompt_toolkit.formatted_text import ANSI
from prompt_toolkit.buffer import Buffer
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout import ScrollablePane,  CompletionsMenu, Float, FloatContainer
from prompt_toolkit.layout.containers import HSplit, Window, to_container
from prompt_toolkit.layout.controls import BufferControl, FormattedTextControl
from prompt_toolkit.layout.layout import Layout
from prompt_toolkit.key_binding.key_processor import KeyPressEvent
from prompt_toolkit.widgets import Frame, Label, TextArea
from rich.console import Console
from prompt_toolkit.completion import CompleteEvent, Completer, Completion
from prompt_toolkit.document import Document
from prompt_toolkit.formatted_text import AnyFormattedText
from typing import Callable, Iterable

from prompt_toolkit.history import InMemoryHistory

class InterfaceCommand:
    def __init__(self, name, description):
        self.name = name
        self.description = description

class DynamicWordCompleter(WordCompleter):
    def __init__(self, callback):
        self.callback = callback
        super().__init__([])
        
    def get_completions(self, document: Document, complete_event: CompleteEvent) -> Iterable[Completion]:
        self.words = self.callback()
        return super().get_completions(document, complete_event)
class Interface:
    def __init__(self):
        self.cmd_info = Label("Hello, world!")
        self.text_area = TextArea(
            text=f"",
            prompt="> ", completer=DynamicWordCompleter(self.generate_completer),
            
        )
        self.commands: list[InterfaceCommand] = []
        self.set_commands(
            InterfaceCommand("test", "test command"),
            InterfaceCommand("help", "help command"),
            InterfaceCommand("exit", "exit command"),
        )
        
        self.text_area.buffer.on_text_changed.add_handler(self.on_text_changed)
        
        self.pane = ScrollablePane(HSplit([
            *[Label(f"Test{i}") for i in range(50)],
            Label("!!!\n@@@\n###\n###\n###\n###")
        ]))
        self.hidden = []
        self.index = 0
        self.kb = KeyBindings()
        self.kb.add("enter")(self.handle_input)
        self.kb.add("c-c")(self.exit_)
        self.kb.add("down")(self.down)
        self.kb.add("up")(self.up)
        self.console = Console(highlight=False)
        
        root = HSplit(
            [
                Frame(self.pane),
                self.cmd_info,
                Frame(self.text_area, height=5),
            ],
        )

        root = FloatContainer(root, floats=[
            Float(
                xcursor=True,
                ycursor=True,
                content=CompletionsMenu(max_height=5, scroll_offset=1),
            ),
        ])
        
        self.root = Layout(container=root)
        app = Application(layout=self.root, key_bindings=self.kb, full_screen=True)
        app.run()
    
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
    
    def add_label(self, string):
        panel: HSplit = self.pane.get_children()[0]
        panel.children.append(to_container(Label(string)))

    def handle_input(self, event: KeyPressEvent):
        text = self.text_area.buffer.text
        self.text_area.buffer.text = ""
        self.add_label(self.format(f"[red]{text}[/]"))
    
        
        self.scroll(self.get_lines())
    
    def format(self, text):
        with self.console.capture() as cap:
            self.console.print(text, end="")
        return ANSI(cap.get())
        
    def get_lines(self):
        panel: HSplit = self.pane.get_children()[0]
        windows: Window = panel.get_children()
        norm = lambda x: x.value if isinstance(x, ANSI) else x
        lines = sum([len(norm(window.content.text()).split('\n')) for window in windows])
        return lines
        
    def scroll(self, amount):
        # print(len(panel.get_children()))
        lines = self.get_lines()
        self.pane.vertical_scroll = min(lines - 30, max(0, self.pane.vertical_scroll + amount))
        
    
    def down(self, event):   
       self.scroll(1)
    
    def up(self, event):
        self.scroll(-1)
            
    def exit_(self, event: KeyPressEvent):
        event.app.exit()


Interface()
