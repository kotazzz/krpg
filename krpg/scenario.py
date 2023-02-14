import shlex

class Section:
    def __init__(self, name, args=None, parent=None):
        self.name = name
        self.children = []
        self.args = args or []
        self.parent = parent
    
    def __repr__(self):
        return f"Section({self.name!r}, {self.args}, {self.children})"
        
class Command:
    def __init__(self, name, args=None):
        self.name = name
        self.args = args or []
    
    def __repr__(self) -> str:
        return f"Command({self.name!r}, {self.args})"


def parse(text):
    text = text.replace("\n\n", "\n")
    lines = text.split("\n")
    lines = [r for line in lines if (r:=line.strip().split("#", 1)[0])]
    curr = Section('root')
    for line in lines:
        if line == "}":
            curr = curr.parent
        elif line.endswith("{"):
            name, *args = shlex.split(line[:-1])
            new = Section(name, args, curr)
            curr.children.append(new)
            curr = new
        
        else:
            cmd, *args = shlex.split(line)
            curr.children.append(Command(cmd, args))
    return curr
    
