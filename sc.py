from calendar import c
from lark import Lark, Transformer
from rich import print
# Загрузка грамматики из файла
grammar = r"""
start: ((command | block))+

command.4: name args END

block.500:  name args "{" body "}"

name: word
args: (WS word)*
body: (command | block)* 

END.2: (NEWLINE | ";" )
word: ESCAPED | UNQUOTED | LONG_STRING
UNQUOTED.0: /[^\s]+/
ESCAPED.1: /[ubf]?r?("(?!"").*?(?<!\\)(\\\\)*?"|'(?!'').*?(?<!\\)(\\\\)*?')/i
LONG_STRING.500: /[ubf]?r?('''.*?(?<!\\)(\\\\)*?''')/is

COMMENT: "/*" /[^\/]*/ "*/"

%import common.WS
%import common.NEWLINE
%ignore WS
%ignore END
%ignore COMMENT
"""




# Создание парсера
parser = Lark(grammar, start='start', parser='earley')#, parser='lalr')

# Примеры команд
commands = [
    'test test',
    'no_args',
    '"Строка 1" "Строка 2"'
]

class Command:
    def __init__(self, name, *args):
        self.name = name
        self.args = list(args)

    def __repr__(self):
        return f"Command({self.name!r}, {self.args})"

class Section:
    def __init__(self, name, args, body):
        self.name = name
        self.args: list[str] = args
        self.body: list[Section|Command] = body

    def __repr__(self):
        return f"Section({self.name!r}, {self.args}, {self.body})"
class CommandTransformer(Transformer):
    def start(self, items):
        return items
    
    def command(self, items):
        # return Command(items[0], *items[1:])
        name, args, _ = items
        return Command(name, *args)
    def block(self, items):
        name, args, body = items
        return Section(items[0], args, body)
    def name(self, items):
        return items[0]
    def args(self, items):
        return [arg for arg in items if arg is not None]
    def body(self, items):
        return items
    def item(self, items):
        return items[0]
    def WS(self, items):
        return None
    def NEWLINE(self, items):
        return None
    def END(self, items):
        return None
    def word(self, items):
        return items[0].value
"""
command
block a b c {
    test 1
    test 2
    test {
        [red]test[/]
    }
}
"""
text= open('krpg/content/map.krpg', 'r', encoding='utf-8').read()+'\n'
tree = parser.parse(text)
result = CommandTransformer().transform(tree)
from rich.console import Console
c = Console(markup=False)
# print(tree)
c.print(result)
