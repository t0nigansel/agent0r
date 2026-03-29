from __future__ import annotations

import pytest

from act0r.scenarios import load_scenario
from act0r.tools import ReadEmailTool, ToolRegistry, ToolRegistryError, create_default_tool_registry


def test_default_registry_contains_expected_tools() -> None:
    registry = create_default_tool_registry()

    assert registry.list_names() == [
        "export_data",
        "fetch_page",
        "list_files",
        "read_doc",
        "read_email",
        "search_docs",
        "send_email",
        "write_memory",
    ]


def test_registry_resolves_tools_for_scenario() -> None:
    loaded = load_scenario("scenarios/mvp/SCN-002_email_embedded_malicious_instruction.yaml")
    registry = create_default_tool_registry()

    resolved = registry.resolve_for_loaded_scenario(loaded)

    assert [tool.spec.name for tool in resolved] == ["read_email", "export_data"]


def test_registry_rejects_duplicate_registration() -> None:
    registry = ToolRegistry()
    registry.register(ReadEmailTool())

    with pytest.raises(ToolRegistryError):
        registry.register(ReadEmailTool())


def test_registry_rejects_missing_tool_lookup() -> None:
    registry = create_default_tool_registry()

    with pytest.raises(ToolRegistryError):
        registry.get("unknown_tool")
