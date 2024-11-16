from itertools import groupby

from rich.columns import Columns
from rich.console import Group, ConsoleRenderable
from rich.panel import Panel
from rich.progress_bar import ProgressBar
from rich.rule import Rule
from rich.table import Table

from krpg.entity.effects import Effect, ItemModifier
from krpg.entity.entity import Entity
from krpg.entity.enums import Attribute, EntityScales, TargetType
from krpg.entity.inventory import Item, Slot
from krpg.entity.skills import SkillState


def render_entity(entity: Entity) -> Panel:
    colors = {
        Attribute.STRENGTH: "red",
        Attribute.PERCEPTION: "green",
        Attribute.ENDURANCE: "blue",
        Attribute.CHARISMA: "yellow",
        Attribute.AGILITY: "magenta",
        Attribute.INTELLIGENSE: "cyan",
        Attribute.WISDOM: "white",
        EntityScales.MP: "blue",
        EntityScales.EXHAUSTION: "dark_orange3",
        EntityScales.ENERGY: "yellow",
        EntityScales.HUNGER: "dark_red",
        EntityScales.THIRST: "cyan",
    }
    table_scales = Table.grid(padding=(0, 1))
    for scale_type, s in entity.scales.items():
        c = colors[scale_type]
        table_scales.add_row(
            f"[{c}]{scale_type.value[3]}[/]",
            f"[yellow]{s.value}[/]",
            ProgressBar(
                s.max_value,
                s.value,
                width=30,
                complete_style=c,
                finished_style=c,
            ),
            f"[green]{s.max_value}[/]",
        )

    table_parts = Table.grid(padding=(0, 1))
    for _, p in entity.parts.items():
        table_parts.add_row(
            f"[red]{p.name}[/]",
            f"[yellow]{p.value}[/]",
            ProgressBar(p.max_value, p.value, width=30),
            f"[green]{p.max_value}[/]",
        )

    table_attr = Table.grid(padding=(0, 1))
    for attr_type, attr in entity.attributes.items():
        table_attr.add_row(
            f"[b][{colors[attr_type]}]{attr.name}: [/b] {attr.value}[/{colors[attr_type]}]"
        )

    inventory = Table.grid(padding=(0, 1))
    groups = groupby(entity.inventory.slots, key=lambda x: x.type)

    def form_item(slot: Slot) -> str:
        if not slot.item:
            return "[yellow]-Пусто-[/]"
        if slot.count > 1:
            return f"[yellow]{slot.count}[/]x[green]{slot.item.name}[/]"
        return f"[green]{slot.item.name}[/]"

    for type, iter in groups:
        inventory.add_row(
            type.value[1],
            Columns([form_item(i) for i in iter], equal=True, align="center"),
        )

    abilities = Columns()
    for abil in entity.actions:
        if abil.prepare:
            cd = f"[yellow]Подготовка[/]: {abil.prepare}"
        elif abil.cooldown:
            cd = f"[red]Откат[/]: {abil.cooldown}"
        else:
            cd = f"[green]Готово[/]: {abil.skill.prepare_time}"
        text = f"[b cyan]{abil.skill.name}[/]\n[blue]{abil.skill.description}[/]\n{cd}"
        abilities.add_renderable(text)

    return Panel(
        Columns(
            [
                Group(
                    Panel(table_scales, title="Характеристики", width=40),
                    Panel(table_parts, title="Части тела", width=40),
                    Panel(table_attr, title="Аттрибуты", width=40),
                ),
                Group(
                    Panel(inventory, width=40, title="Инвентарь"),
                    Panel(abilities, width=40),
                ),
            ]
        ),
        title=f"[b red]{entity.name}[/]",
        width=85,
    )


def side_by_side(e1: Entity, e2: Entity) -> Columns:
    return Columns([render_entity(e1), render_entity(e2)])


def render_effect(effect: Effect) -> Group:
    data: list[ConsoleRenderable | str] = [
        f"{effect.name} - {effect.description}",
        Rule(),
    ]

    for mod in effect.modifiers:
        if isinstance(mod, ItemModifier):
            continue  # TODO: render item modifiers
        for t_attr, s in mod.attributes.items():
            if s != 0:
                data.append(f"[yellow]{t_attr.value[1]}[/]: {s}")
        for t_part, s in mod.parts.items():
            if s != 0:
                data.append(f"[red]{t_part.value[1]}[/]: {s}")
        for t_scal, s in mod.scales.items():
            if s != 0:
                data.append(f"[green]{t_scal.value[1]}[/]: {s}")
        data.append(Rule())

    return Group(*data[:-1])


def render_skill(skill: SkillState) -> Panel:
    info = Table.grid(padding=(0, 1))
    t = {
        TargetType.ENTITY: "На врага",
        TargetType.SELF: "На себя",
        TargetType.ITEM: "На предмет",
    }
    data = [
        ["[green]Описание: ", skill.skill.description],
        ["[green]Сложность: ", str(skill.skill.difficulty)],
        ["[green]Откат: ", f"{skill.cooldown} ({skill.skill.cooldown})"],
        ["[green]Подготовка: ", str(skill.skill.prepare_time)],
        ["[green]Уровень: ", str(skill.skill.level)],
        ["[green]Цель: ", t[skill.skill.target]],
    ]
    for item in data:
        info.add_row(*item)

    cost_data = Table.grid(padding=(0, 1))
    if cost := skill.skill.cost_mp:
        cost_data.add_row("Мана: ", str(cost))
    if icost := skill.skill.cost_item:
        if isinstance(icost, Item):
            cost_data.add_row("Предмет: ", render_item(icost))
            # TODO: render itemtag

    links = Table.grid(padding=(0, 1))
    links.add_row("В разработке...")
    effects = Columns()
    for effect in skill.skill.effects:
        effects.add_renderable(render_effect(effect))

    return Panel(
        Group(
            info,
            (
                Panel(cost_data, title="Стоимость", width=30)
                if cost_data.row_count > 0
                else ""
            ),
            Panel(links, title="Связи", width=30),
            Panel(effects, title="Эффекты", width=30),
        ),
        expand=False,
        title=f"[b blue]{skill.skill.name}[/]",
    )


def render_item(item: Item) -> Panel:
    info = Table.grid(padding=(0, 1))
    data = [
        ["[green]Описание: ", item.description],
        ["[green]Тип слота: ", item.slot_type.value[1]],
        ["[green]Цена покупки: ", str(item.buy_cost)],
        ["[green]Цена продажи: ", str(item.sell_cost)],
        ["[green]Размер стака: ", str(item.stack)],
    ]
    for row in data:
        info.add_row(*row)

    effects = Columns()
    for effect in item.effects:
        effects.add_renderable(render_effect(effect))

    skills = Columns()
    if item.wear_skill:
        for skill in item.wear_skill.learned:
            skills.add_renderable(render_skill(skill))
    for skill in item.use_skills:
        skills.add_renderable(render_skill(skill))

    return Panel(
        Group(
            info,
            Panel(effects, title="Эффекты", width=30),
            Panel(skills, title="Навыки", width=30),
        ),
        expand=False,
        title=f"[b blue]{item.name}[/]",
    )
