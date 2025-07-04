from rich.panel import Panel
from rich.table import Table
from rich.console import Group
from krpg.engine.world import LocationState


def render_location_info(loc: LocationState) -> Panel:
    items = Table.grid(padding=(0, 1))
    if loc.items:
        items.add_row("[cyan]Предметы:[/]")
    for slot in loc.items:
        assert slot.item
        items.add_row(f"[blue]•[/] [green]{slot.item.name}[/] x [yellow]{slot.count}")

    npcs = Table.grid(padding=(0, 1))
    if loc.npcs:
        npcs.add_row("[cyan]Рядом:[/]")
    for npc in loc.npcs:
        npcs.add_row(f"[blue]•[/] [green]{npc.npc.name}[/] - [yellow]{npc.npc.description}")

    actions = Table.grid(padding=(0, 1))
    if loc.actions:
        actions.add_row("[cyan]Действия:[/]")
    for action in loc.actions:
        actions.add_row(f"[blue]•[/] [green]{action.name}[/] - [yellow]{action.description}")

    return Panel(
        Group(
            f"[cyan]Описание: [/]{str(loc.location.description)}",
            items,
            npcs,
            actions,
        ),
        title=f"[b blue]{loc.location.name}[/]",
    )
