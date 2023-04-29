from __future__ import annotations
from itertools import groupby
import random
from textwrap import wrap
import msgpack
import zlib
from krpg.bestiary import Bestiary
from krpg.clock import Clock
from krpg.console import KrpgConsole
from krpg.actions import ActionManager, action
from krpg.events import EventHandler
from krpg.presenter import Presenter
from krpg.scenario import parse
from krpg.encoder import Encoder
from krpg.executer import Executer
from krpg.player import Player
from krpg.builder import Builder
from krpg.settings import Settings
from krpg.world import World
from rich.spinner import Spinner

from rich.live import Live
import time
from krpg.events import Events
__version__ = "8B"
DEBUG = True


class Game:
    version = __version__
    debug = DEBUG
    splashes = [
            "Кто придумал эту игру?",
            "Да, это игра.",
            "Мне нравится эта игра.",
            "Ну, это, конечно, игра.",
            "Это игра.",
            "Я думаю, это игра.",
            "О, это игра!",
            "Это игра? Да, это игра!",
            "Привет, мир!",
            "rm -rf / --no-preserve-root",
            "Как тебя зовут?",
            "Как дела?",
            "Как тебе игра?",
            "Ой, это игра!",
            "UNO reverse card",
            "UNO draw 4 card",
            "UNO wild card",
            "UNEXPECTED TOKEN",
            "ERROR 404",
            "ERROR 500",
            "Удаление системных файлов...",
            "Встречай орду гоблинов!",
            "Ты настолько сильный, что медведи даже не смеют драться с тобой!",
            "Новый день, новые приключения!",
            "Кажется, я видел дракона в той пещере...",
            "Простите, я только наблюдаю за битвой.",
            "Думаешь, ты можешь победить меня словами? Попробуй!",
            "Что-то мне говорит, что ты сейчас идешь на смерть...",
            "Не считай, что я просто стена.",
            "Кто-то раньше сделал твою задачу. Но это был не ты.",
            "Ой! Кажется, я кое-кого разозлил...",
            "Осторожно, здесь много ловушек!",
            "Внимание, враги на горизонте!",
            "Ух, какой приятный запах эльфийской магии!",
            "Кто-то меня вызвал? О, нет. Это просто порыв ветра.",
            "Твоя мама говорит, что ты воин, но ты скорее похож на мага.",
            "Когда-то я был королем гномов. Но это было давно.",
            "Вы любите приключения? Я тоже люблю приключения!",
            "Не знаю, что ты ищешь, но кажется, оно не там, где вы думаете.",
            "Если бы у меня были руки, я бы помог вам открыть эту дверь.",
            "Ты не прошел испытание огнем, пока не пережил испытание замерзания.",
            "В мире есть много сокровищ. И много смертельных ловушек, охраняющих их.",
            "Как говорится, лучше один раз увидеть, чем сто раз услышать.",
            "Осторожно, на этой земле затаилась магия темной стороны.",
            "Не забудь захватить мантию Невидимости. Может пригодится.",
            "Я не говорю, что ты должен помочь мне, но если ты не поможешь, мы оба можем умереть.",
            "Вы нашли сундук, но там только промокшая носовая платок",
            "Скелет уронил свою ногу и попросил вас ее поднять",
            "Чудовище оказалось вегетарианцем и ушло, разочарованное",
            "Вы встретили гоблина-бухгалтера. Он просит вас заполнить налоговую декларацию",
            "Вас оглушил удар по голове. Вы просыпаетесь в тюрьме за нарушение закона о запрете ношения фиолетовых штанов",
            "Вы нашли бутылку, внутри которой оказался исчезнувший градусник",
            "Гном-механик починил вам меч, но теперь он меняет цвет каждые 5 минут",
            "Вы попали в ловушку. Но вам повезло: это ловушка для ловушек",
            "Крыса украла у вас все деньги и принесла обратно целую кучу грязного белья",
             "Вы встретили дракона, который оказался гипнотизером. Теперь вы уверены, что вы – курочка ряба",
             "Вы нашли лук, но он оказался из пластика",
             "Вы нашли карту сокровищ, но все места на ней отмечены как 'здесь ничего нет'",
             "Вы нашли колоду карт, но все они дамы",
             "Вы нашли кота, который оказался инопланетной формой жизни",
             "Вы нашли статую, которая оказалась просто манекеном",
             "Вы нашли книгу, но в ней все страницы пустые",
             "Вы нашли магический кристалл, но он оказался всего лишь обычной галькой",
             "Вы нашли меч, но он оказался слишком тяжелым для вас",
             "Вы нашли зелье лечения, но оно оказалось ядом",
             "Вы попали в ловушку, но вас спасла маленькая мышь, которая прогрызла дыру в стене",
             "Вы нашли длинную трещину в земле. Оказалось, что это просто международная граница",
             "Вы нашли голову медузы, но все ее щупальца оказались сломаны",
             "Вы нашли птицу, которая оказалась обычным дроном",
             "Вы нашли вещь, которая оказалась слишком большой, чтобы ее можно было поднять",
             "Вы нашли печенье, которое говорит вам, что вы проиграли",
             "Вы нашли волшебную палочку, которая оказалась просто палкой",
             "Вы нашли ворона, который оказался просто перышком",
             "Вы нашли красивый камень, но он оказался слишком тяжелым, чтобы его можно было поднять",
             "Вы нашли лук, но он оказался из белого шоколада",
             "Вы нашли книгу заклинаний, но все они оказались на языке, который вы не знаете",
             "Вы нашли гробницу, но там оказалась только просто гробница",
             "Вы нашли золотую монету, но она оказалась фальшивой",
             "Вы нашли карту мира, но на ней было только одно место: в котором вы находитесь",
             "Вы нашли магический камень, но он оказался просто куском стекла",
             "Вы нашли рыцарскую броню, но она оказалась слишком мала для вас",
             "Вы нашли волшебный меч, но он оказался слишком коротким, чтобы наносить урон",
             "Вы нашли свиток с магическим заклинанием, но он оказался написан на языке программирования",
             "Вы нашли книгу о приключениях, но она оказалась просто каталогом IKEA",
             "Вы нашли зелье восстановления маны, но оно оказалось просто газировкой",
             "Вы нашли волшебную шляпу, но она оказалась слишком мала для вашей головы",
             "Вы нашли магический кристалл, но он оказался просто куском льда",
             "Вы нашли дверь, но за ней ничего не было",
             "Вы нашли книгу с картинками, но все страницы были пустые",
             "Вы нашли магический посох, но он оказался просто палкой для селедки",
             "Вы нашли кинжал, но он оказался слишком тупым, чтобы наносить урон",
             "Вы нашли зелье лечения, но оно оказалось горькой медицинской настойкой",
             "Вы нашли книгу, в которой все страницы были написаны наоборот",
             "Вы нашли книгу о драконах, но она оказалась просто каталогом драконьей посуды",
             "Вы нашли мешок с золотом, но оказалось, что он был просто мешком с песком",
             "Вы нашли магический амулет, но он оказался просто обычной каменной круглой бусиной",
    ]
    def set_debug(self):
        self.log.setLevel(self.debug * 5)

    def __init__(self):
        
        self.console = KrpgConsole()
        
        if self.debug:
            spin = Spinner('dots10', text='test', style="green")
            with Live(spin, refresh_per_second=20) as live:
                _reserve = self.console.log.debug
                def func(t):
                    spin.update(text=t)
                    time.sleep(0.2)
                self.console.log.debug = func
                self.init_game(lambda t: spin.update(text=t))
                self.console.log.debug = _reserve
        else:
            self.init_game(self.log.debug)
            
    def init_game(self, debug):
            self.state = "none"
            self.start_time = self.save_time = self.timestamp()
            self.log = self.console.log
            self.set_debug()

            self.actions = ActionManager()
            debug(f"Init [green]ActionManager[/]: {self.actions}")

            self.add_actions(self)
            self.encoder = Encoder()
            debug(f"Init [green]Encoder[/]: {self.encoder}")

            self.events = EventHandler(locked=True)
            debug(f"Init [green]EventHandler[/]: {self.events}")

            for attr in filter(lambda x: x.startswith("on_"), dir(self)):
                cb = getattr(self, attr)
                self.events.listen(attr[3:], cb)
                debug(f"Added [red]listener[/] for {attr[3:]}")

            scenario = open("scenario.krpg").read()
            self.scenario_hash = f"{zlib.crc32(scenario.encode()):x}"
            self.scenario = parse(scenario)
            debug(f"Loaded scenario with {len(self.scenario.children)} items")

            self.savers: dict[str, set[callable, callable]] = {}
            
            self.settings = Settings(self)
            debug(f"Init [green]Settings[/]: {self.settings}")
            
            self.executer = Executer(self)
            debug(f"Init [green]Executer[/]: {self.executer}")

            self.player = Player(self)
            debug(f"Init [green]Player[/]: {self.player}")

            self.presenter = Presenter(self)
            debug(f"Init [green]Presenter[/]: {self.presenter}")

            self.bestiary = Bestiary(self)
            debug(f"Init [green]Bestiary[/]: {self.bestiary}")

            self.clock = Clock(self)
            debug(f"Init [green]Clock[/]: {self.clock}")

            self.world = World(self)
            debug(f"Init [green]World[/]: {self.world}")

            self.builder = Builder(self)
            debug(f"Starting build world...")
            

            self.builder.build()

    def timestamp(self):
        return int(time.time()) - 1667250000  # 1 Nov 2022 00:00 (+3)

    def add_actions(self, obj: object):
        self.log.debug(f"Add submanager {obj}")
        self.actions.submanagers.append(obj)

    @action("help", "Показать команды", "Игра")
    def action_help(game: Game):
        actions = sorted(game.actions.get_actions(), key=lambda x: x.category)
        cmdcat = groupby(actions, key=lambda x: x.category)
        for cat, cmds in cmdcat:
            game.console.print(f"[b red]{cat}")
            for cmd in cmds:
                game.console.print(f" [green]{cmd.name}[/] - {cmd.description}")

    @action("credits", "Авторы и благодарности", "Игра")
    def action_credits(game: Game):
        game.console.print(
            "[green]Автор:[/] Kotaz\n"
            "[green]Язык:[/] Python 3\n"
            "[green]Библиотеки:[/] rich, prompt_toolkit, msgpack\n"
            "[green]Кол-во строк кода:[/] 1000+\n\n"
            "[bold green]Отдельная благодарность:[/]\n"
            "  [green]Никто[/]\n"
            "  [red]Конец[/]\n"
        )

    @action("guide", "Игровая справка", "Игра")
    def action_guide(game: Game):
        passages = {
            "FAQ": ("Тут пусто :("),
            "Changelog": ("Мне [red]лень[/] тут что-то писать... :( \n"),
            "Мне нужна помощь по командам": (
                "Используйте [green]help[/] или [green]guide[/] для получения справки\n"
            ),
            "[blue][AUTO][/] и аргументы": (
                "В игре все действия используют лишь одну фразу или слово. "
                "У них нет аргументов или какого либо синтаксиса. "
                "Если для определенного действия требуются аргументы - "
                "они будут запрошенные через отдельные поля ввода. Теперь "
                "вам не надо заучивать сложный синтаксис дял простых действий. "
                "Хотите ввести аргументы сразу? Разделяйте свои действия пробелом. "
                "Игра запоминает каждое слово отдельно и как только понадобится что-то "
                "ввести она сама вставит то, что вы вводили ранее. "
                "Таким образом вы можете одновременно вводить множество "
                "команд за раз и они все исполнятся сами\n"
                "Попробуйте ввести [green]e guide 1[/] и вы выйдете из "
                "справки и вернетесь, открыв первую страницу"
            ),
        }
        while True:
            game.console.print("[bold green]Гайды и справка[/]")
            game.console.print("[green]Выберите секцию (e - Выход)[/]")
            select = game.console.menu(2, list(passages.items()), "e", lambda x: x[0])
            if not select:
                return
            else:
                text = wrap(select[1], replace_whitespace=False)
                game.console.print("\n".join(text))

    @action("exit", "Выйти из игры", "Игра")
    def action_exit(game: Game):
        game.state = "exit"

    @action("save", "Сохранить игру", "Игра")
    def action_save(game: Game):
        game.events.dispatch(Events.SAVE)

    @action("load", "Загрузить игру", "Игра")
    def action_load(game: Game):
        game.events.dispatch(Events.LOAD)

    @action("about", "Загрузить игру", "Игра")
    def action_load(game: Game):
        game.show_logo()
        game.console.print("[b green]Описание[/]: [blue]KRPG[/]")
        game.console.print("[b blue]Автор[/]: [green]Kotaz[/]")
        game.console.print("[b yellow]Язык[/]: [red]python[/]")
        game.console.print("[b black on green]Вас ждет увлекательное путешествие по миру, где Вы будете сражаться\n"
                           " с монстрами, выполнять квесты и становиться все\n"
                           " сильнее и сильнее. Сможете ли Вы стать настоящим героем?[/]")

    def add_saver(self, name: str, save: callable, load: callable):
        def add_message(func, message):
            def deco(*args, **kwargs):
                self.log.debug(message)
                return func(*args, **kwargs)

            return deco

        self.log.debug(f"Added Savers {name!r}")
        self.savers[name] = (
            add_message(save, f"Saving {name}"),
            add_message(load, f"Loading {name}"),
        )

    def on_state_change(self, state):
        self.state = state

    def on_save(self):
        self.save_time = self.timestamp()
        data = {name: funcs[0]() for name, funcs in self.savers.items()}
        bdata = msgpack.packb(data)
        zdata = zlib.compress(bdata, level=9)
        select = self.console.menu(5, list(self.encoder.abc.keys()))
        encoded = self.encoder.encode(zdata, type=select)
        self.log.debug(f"Data: {data}")
        self.log.debug(f"BinData ({len(bdata)}): {bdata.hex()}")
        self.log.debug(
            f"Zipped from {len(bdata)} to {len(zdata)}, string: {len(encoded)}"
        )
        self.console.print(f"[green]Код сохранения: [yellow]{list(self.encoder.abc.keys()).index(select)}{encoded}[/]")

    def on_load(self, failcb=None, successcb=None):
        while True:
            self.console.print("[green]Введите код сохранения (e - выход):")
            encoded = self.console.prompt(2, raw=True)
            try:
                if encoded == "e":
                    break
                select, encoded = encoded[0], encoded[1:]
                select = list(self.encoder.abc.keys())[int(select)]
                zdata = self.encoder.decode(encoded, type=select)
                bdata = zlib.decompress(zdata)
                data = msgpack.unpackb(bdata)
                for name, funcs in self.savers.items():
                    funcs[1](data[name])
            except Exception as e:
                self.console.print(f"[red]Ошибка при загрузке игры: {e}[/]")
                if not self.debug:
                    self.log.exception(e)
            else:
                self.console.print("[green]Игра загружена[/]")
                if successcb:
                    successcb()
                    self.events.dispatch(Events.LOAD_DONE)
                return

        if failcb:
            failcb()

    def on_event(self, event, *args, **kwargs):
        self.log.debug(f"[b yellow]{event}[/] {args} {kwargs}")

    def on_command(self, command):
        actions = self.actions.get_actions()
        cmds = {cmd.name: cmd for cmd in actions}
        if command in cmds:
            cmds[command].callback(self)
            self.clock.wait(cmds[command].time)
        else:
            self.console.print(f"[red]Неизвестная команда {command}[/]")
            self.console.print(f"[green]Доступные команды: {' '.join(cmds.keys())}[/]")

    def main(self):
        try:
            self.run()
        except Exception as e:
            self.log.exception(e)
    def show_logo(self):
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
            "[magenta]K[/][red]-[/][blue]R[/][yellow]P[/][green]G[/] - Вас ждет увлекательное путешествие по миру, \n"
            "где Вы будете сражаться с монстрами, выполнять квесты и становиться\n"
            "все сильнее и сильнее. Сможете ли Вы стать настоящим героем?\n"
        )
    def run(self):
        self.log.debug("Hello, world!")
        self.events.unlock()
        c = self.console
        success = lambda: self.events.dispatch(Events.STATE_CHANGE, state="playing")
        
        clrs = [
            "[bold magenta]",
            "[bold red]",
            "[bold blue]",
            "[bold yellow]",
            "[bold green]",
        ]
        self.console.print(random.choice(clrs) + random.choice(self.splashes))
        self.show_logo()
        while self.state != "playing":
            menu = {
                'start': 'Начать новую игру',
                'load': 'Загрузить сохранение',
                'credits': 'Авторы игры',
                'about': 'Об игре', 
                'settings': 'Настройки игры',
                'exit': 'Выйти'
            }
            select = self.console.menu(5, list(menu.keys()), view=lambda k: f'{menu[k]}', title="[green b]Игровое меню")
            if select == 'load':
                self.events.dispatch(Events.LOAD, successcb=success)
            elif select == 'start':
                c.print(
            "Задать имя персонажу можно [red]только один раз[/]!\n"
            "  [blue]help[/] - Показать список команд\n"
            "  [blue]guide[/] - Справка и помощь, как начать\n")
                c.print(f"[green]Введите имя:[/]")
                self.player.name = c.prompt(2)
                success()
            elif select == 'exit':
                exit()
            else:
                self.events.dispatch(Events.COMMAND, command=select)
        try:
            while self.state != 'exit':
                actions = self.actions.get_actions()
                cmds_data = {cmd.name: cmd.description for cmd in actions}
                cmd = c.prompt(1, cmds_data)
                self.events.dispatch(Events.COMMAND, command=cmd)

        except KeyboardInterrupt:
            c.print("[red]Выход из игры[/]")

    def __repr__(self):
        return "<Game>"
