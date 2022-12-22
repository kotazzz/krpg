from krpg.console import Console


class Game:
    def __init__(self):
        self.console = Console()
        
        self.run()
    
    def splash(self):
        clrs = [
                "[bold magenta]",
                "[bold red]",
                "[bold blue]",
                "[bold yellow]",
                "[bold green]",
            ]
        self.console.print(
            (
                "{0}╭───╮ ╭─╮{1}       {2}╭──────╮  {3}╭───────╮{4}╭───────╮\n"
                "{0}│   │ │ │{1}       {2}│   ╭─╮│  {3}│       │{4}│       │\n"
                "{0}│   ╰─╯ │{1}╭────╮ {2}│   │ ││  {3}│   ╭─╮ │{4}│   ╭───╯\n"
                "{0}│     ╭─╯{1}╰────╯ {2}│   ╰─╯╰─╮{3}│   ╰─╯ │{4}│   │╭──╮\n"
                "{0}│     ╰─╮{1}       {2}│   ╭──╮ │{3}│   ╭───╯{4}│   ││  │\n"
                "{0}│   ╭─╮ │{1}       {2}│   │  │ │{3}│   │    {4}│   ╰╯  │\n"
                "{0}╰───╯ ╰─╯{1}       {2}╰───╯  ╰─╯{3}╰───╯    {4}╰───────╯\n".format(
                    *clrs
                )
            )
        )
        self.console.print(
            "[magenta]K[red]-[blue]R[yellow]P[green]G[/] - Рпг игра, где вы изучаете мир и совершенствуетесь\n"
            "Сохранения доступны [red]только[/] в этой локации\n"
            "Задать имя персонажу можно [red]только один раз[/]!\n"
            "  [blue]help[/] - Показать список команд\n"
            "  [blue]guide[/] - Справка и помощь, как начать\n"
            "  [blue]bestiary[/] - Показать информацию о здешних монстрах\n",
            min=0.002,
        )
    
    def run(self):
        self.splash()
        self.console.print("[green]Hello, world![/]")
        
        

Game()