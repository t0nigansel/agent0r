from __future__ import annotations

from typing import Dict, Iterable, List

from act0r.scenarios.models import LoadedScenario, Scenario

from .base import Tool
from .errors import ToolRegistryError
from .fake_tools import build_default_fake_tools


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: Dict[str, Tool] = {}

    def register(self, tool: Tool) -> None:
        name = tool.spec.name
        if name in self._tools:
            raise ToolRegistryError("Tool already registered: {}".format(name))
        self._tools[name] = tool

    def get(self, name: str) -> Tool:
        if name not in self._tools:
            raise ToolRegistryError("Unknown tool: {}".format(name))
        return self._tools[name]

    def list_names(self) -> List[str]:
        return sorted(self._tools.keys())

    def resolve(self, names: Iterable[str]) -> List[Tool]:
        return [self.get(name) for name in names]

    def resolve_for_scenario(self, scenario: Scenario) -> List[Tool]:
        names = [tool.name for tool in scenario.tools]
        return self.resolve(names)

    def resolve_for_loaded_scenario(self, loaded_scenario: LoadedScenario) -> List[Tool]:
        return self.resolve_for_scenario(loaded_scenario.scenario)


def create_default_tool_registry() -> ToolRegistry:
    registry = ToolRegistry()
    for tool in build_default_fake_tools():
        registry.register(tool)
    return registry
