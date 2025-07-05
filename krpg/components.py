from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from krpg.actions import ActionManager
    from krpg.engine.executer import Extension
    from krpg.events import Listener


type Component = type[ActionManager] | type[Extension] | Listener
type RegisteredComponent = ActionManager | Extension | Listener


class ComponentRegistry:
    def __init__(self) -> None:
        self.components: dict[type[RegisteredComponent], list[RegisteredComponent]] = {}

    def register(self, component: RegisteredComponent) -> None:
        self.components.setdefault(type(component), []).append(component)


registry = ComponentRegistry()


def component(item: Component) -> Component:
    if isinstance(item, type):
        registry.register(item())
    else:
        registry.register(item)
    return item
