from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from krpg.actions import ActionManager
    from krpg.engine.executer import Extension
    from krpg.events import Listener


type Component = type[ActionManager] | type[Extension] | Listener


class ComponentRegistry:
    def __init__(self) -> None:
        self.components: list[Component] = []

    def register(self, component: Component) -> None:
        self.components.append(component)


registry = ComponentRegistry()


def component(cls: Component) -> Component:
    registry.register(cls)
    return cls
