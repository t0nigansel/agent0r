from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from .base import BaseTool
from .models import RiskLevel, ToolExecutionContext, ToolSpec

REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_TOOL_FIXTURE_ROOT = REPO_ROOT / "fixtures" / "tools"


class ReadEmailTool(BaseTool):
    spec = ToolSpec(name="read_email", risk_level=RiskLevel.LOW)

    def execute(
        self,
        arguments: Optional[Dict[str, Any]] = None,
        context: Optional[ToolExecutionContext] = None,
    ):
        args = arguments or {}
        ctx = context or ToolExecutionContext()

        content = args.get("content") or ctx.fixtures.get("inbox_email")
        if content is None:
            content = _read_text_fixture(_fixture_root(ctx), "email/sample_email.txt")

        return self._result(
            {
                "email_id": args.get("email_id", "fixture-email"),
                "content": content,
            }
        )


class SearchDocsTool(BaseTool):
    spec = ToolSpec(name="search_docs", risk_level=RiskLevel.LOW)

    def execute(
        self,
        arguments: Optional[Dict[str, Any]] = None,
        context: Optional[ToolExecutionContext] = None,
    ):
        args = arguments or {}
        ctx = context or ToolExecutionContext()

        payload = ctx.fixtures.get("search_results")
        if payload is None:
            payload = _read_json_fixture(_fixture_root(ctx), "search/sample_results.json")

        results = payload.get("results", []) if isinstance(payload, dict) else payload

        return self._result(
            {
                "query": args.get("query", payload.get("query", "")) if isinstance(payload, dict) else args.get("query", ""),
                "results": results,
            }
        )


class FetchPageTool(BaseTool):
    spec = ToolSpec(name="fetch_page", risk_level=RiskLevel.LOW)

    def execute(
        self,
        arguments: Optional[Dict[str, Any]] = None,
        context: Optional[ToolExecutionContext] = None,
    ):
        args = arguments or {}
        ctx = context or ToolExecutionContext()

        content = args.get("content") or ctx.fixtures.get("page_content")
        if content is None:
            content = _read_text_fixture(_fixture_root(ctx), "page/sample_page.txt")

        return self._result(
            {
                "url": args.get("url", "https://example.local/policy"),
                "content": content,
            }
        )


class WriteMemoryTool(BaseTool):
    spec = ToolSpec(
        name="write_memory",
        risk_level=RiskLevel.HIGH,
        has_side_effects=True,
        requires_confirmation=True,
    )

    def execute(
        self,
        arguments: Optional[Dict[str, Any]] = None,
        context: Optional[ToolExecutionContext] = None,
    ):
        args = arguments or {}
        key = args.get("key", "note")
        value = args.get("value", "")

        return self._result(
            {
                "stored": False,
                "key": key,
                "value": value,
                "storage": "disabled_in_fake_tool",
            },
            blocked=True,
            message="write_memory is sandboxed and does not persist state in MVP.",
        )


class ExportDataTool(BaseTool):
    spec = ToolSpec(
        name="export_data",
        risk_level=RiskLevel.HIGH,
        has_side_effects=True,
        requires_confirmation=True,
    )

    def execute(
        self,
        arguments: Optional[Dict[str, Any]] = None,
        context: Optional[ToolExecutionContext] = None,
    ):
        args = arguments or {}
        ctx = context or ToolExecutionContext()

        source = args.get("dataset") or ctx.fixtures.get("customer_snapshot")
        if source is None:
            source = "customer_id,name,region\n1001,Ana,EU"

        return self._result(
            {
                "requested_dataset": args.get("dataset_name", "customer_snapshot"),
                "preview": source,
                "exported": False,
            },
            blocked=True,
            message="export_data is sandboxed and cannot perform outbound export.",
        )


class SendEmailTool(BaseTool):
    spec = ToolSpec(
        name="send_email",
        risk_level=RiskLevel.HIGH,
        has_side_effects=True,
        requires_confirmation=True,
    )

    def execute(
        self,
        arguments: Optional[Dict[str, Any]] = None,
        context: Optional[ToolExecutionContext] = None,
    ):
        args = arguments or {}

        return self._result(
            {
                "to": args.get("to", ""),
                "subject": args.get("subject", ""),
                "body": args.get("body", ""),
                "sent": False,
            },
            blocked=True,
            message="send_email is sandboxed and drafts only in MVP.",
        )


class ListFilesTool(BaseTool):
    spec = ToolSpec(name="list_files", risk_level=RiskLevel.LOW)

    def execute(
        self,
        arguments: Optional[Dict[str, Any]] = None,
        context: Optional[ToolExecutionContext] = None,
    ):
        args = arguments or {}
        ctx = context or ToolExecutionContext()
        root = _fixture_root(ctx)

        files = sorted(
            str(path.relative_to(root))
            for path in root.rglob("*")
            if path.is_file()
        )

        return self._result(
            {
                "scope": args.get("scope", "safe_fixture_root"),
                "files": files,
            }
        )


class ReadDocTool(BaseTool):
    spec = ToolSpec(name="read_doc", risk_level=RiskLevel.LOW)

    def execute(
        self,
        arguments: Optional[Dict[str, Any]] = None,
        context: Optional[ToolExecutionContext] = None,
    ):
        args = arguments or {}
        ctx = context or ToolExecutionContext()

        content = args.get("content") or ctx.fixtures.get("project_brief") or ctx.fixtures.get("document")
        if content is None:
            content = _read_text_fixture(_fixture_root(ctx), "documents/sample_doc.txt")

        return self._result(
            {
                "doc_id": args.get("doc_id", "fixture-doc"),
                "content": content,
            }
        )


def build_default_fake_tools() -> List[BaseTool]:
    return [
        ReadEmailTool(),
        SearchDocsTool(),
        FetchPageTool(),
        WriteMemoryTool(),
        ExportDataTool(),
        SendEmailTool(),
        ListFilesTool(),
        ReadDocTool(),
    ]


def _fixture_root(context: ToolExecutionContext) -> Path:
    return context.safe_fixture_root or DEFAULT_TOOL_FIXTURE_ROOT


def _read_text_fixture(root: Path, relative_path: str) -> str:
    return (root / relative_path).read_text(encoding="utf-8")


def _read_json_fixture(root: Path, relative_path: str) -> Dict[str, Any]:
    return json.loads((root / relative_path).read_text(encoding="utf-8"))
