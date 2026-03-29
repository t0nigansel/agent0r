from __future__ import annotations

from pathlib import Path

import pytest

from act0r.tools import (
    ExportDataTool,
    FetchPageTool,
    ListFilesTool,
    ReadDocTool,
    ReadEmailTool,
    SearchDocsTool,
    SendEmailTool,
    ToolExecutionContext,
    TrustLevel,
    WriteMemoryTool,
)


def test_fake_tools_return_untrusted_metadata() -> None:
    tools = [
        ReadEmailTool(),
        SearchDocsTool(),
        FetchPageTool(),
        WriteMemoryTool(),
        ExportDataTool(),
        SendEmailTool(),
        ListFilesTool(),
        ReadDocTool(),
    ]

    for tool in tools:
        result = tool.execute()
        assert result.tool_name == tool.spec.name
        assert result.trust_level == TrustLevel.UNTRUSTED


def test_read_email_uses_fixture_context_when_provided() -> None:
    tool = ReadEmailTool()
    context = ToolExecutionContext(fixtures={"inbox_email": "fixture body"})

    result = tool.execute(context=context)

    assert result.output["content"] == "fixture body"


@pytest.mark.parametrize(
    "tool",
    [WriteMemoryTool(), ExportDataTool(), SendEmailTool()],
)
def test_high_risk_side_effect_tools_are_sandbox_blocked(tool) -> None:
    result = tool.execute(arguments={"value": "unsafe"})

    assert result.has_side_effects is True
    assert result.requires_confirmation is True
    assert result.blocked is True


def test_list_files_is_scoped_to_safe_fixture_root() -> None:
    safe_root = Path(__file__).resolve().parents[2] / "fixtures" / "tools"
    tool = ListFilesTool()

    result = tool.execute(context=ToolExecutionContext(safe_fixture_root=safe_root))
    files = result.output["files"]

    assert "documents/sample_doc.txt" in files
    assert all(not file_path.startswith("/") for file_path in files)


def test_search_docs_loads_json_fixture_shape() -> None:
    result = SearchDocsTool().execute()

    assert isinstance(result.output["results"], list)
    assert result.output["results"][0]["title"]
