from typing import Any


def render_marked(items: list[Any]) -> str:
    return "\n".join(f"[blue]•[/] {item}" for item in items)
