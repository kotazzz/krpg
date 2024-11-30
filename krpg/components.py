from krpg.actions import ActionManager
from krpg.engine.executer import Extension


Component = ActionManager | Extension


class ComponentRegistry:
    def __init__(self) -> None:
        self.components: list[type[Component]] = []

    def register(self, component: type[Component]) -> None:
        self.components.append(component)


registry = ComponentRegistry()


def component(cls: type[Component]) -> type[Component]:
    assert issubclass(cls, Component), f"{cls} must be {Component}"
    registry.register(cls)
    return cls
