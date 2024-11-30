from rich.panel import Panel
from rich.table import Table
from rich.console import Group
from krpg.engine.world import Location


def render_location_info(loc: Location) -> Panel:
    items = Table.grid(padding=(0, 1))
    for item, count in loc.items:
        items.add_row(f"[blue]•[/] [green]{item.name}[/] x [yellow]{count}")

    npcs = Table.grid(padding=(0, 1))
    for npc in loc.npcs:
        npcs.add_row(str(npc))

    return Panel(
        Group(
            f"[green]Описание: [/]{str(loc.description)}",
            items,
            npcs,
        ),
        title=f"[b blue]{loc.name}[/]",
    )
