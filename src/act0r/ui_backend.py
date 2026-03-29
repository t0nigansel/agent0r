from __future__ import annotations

import json
from dataclasses import dataclass
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Dict, List, Optional
from uuid import uuid4
from urllib.parse import urlparse

from act0r.adapters import AdapterRequest, AdapterResponse, AdapterToolCall, AgentAdapter
from act0r.reporting import MarkdownReportGenerator
from act0r.runner import AgentRunner
from act0r.scenarios import load_scenarios_from_directory
from act0r.storage import SQLiteStorage
from act0r.tools import create_default_tool_registry


DEFAULT_TARGETS = [
    {
        "name": "local-mock",
        "type": "deterministic",
        "status": "ready",
        "description": "Local deterministic adapter for safe evaluation.",
    },
    {
        "name": "ollama-local",
        "type": "adapter",
        "status": "not_connected",
        "description": "Local Ollama adapter profile.",
    },
]


class DeterministicUiAdapter(AgentAdapter):
    def generate(self, request: AdapterRequest) -> AdapterResponse:
        if request.step_index == 0 and request.available_tools:
            tool_name = request.available_tools[0].name
            return AdapterResponse(
                assistant_text="Planning to call {}.".format(tool_name),
                tool_calls=[AdapterToolCall(name=tool_name, arguments={})],
                is_final=False,
            )
        return AdapterResponse(
            assistant_text="Run completed.",
            tool_calls=[],
            is_final=True,
        )


class UiDataService:
    def __init__(
        self,
        *,
        db_path: Path,
        scenario_dir: Path,
        report_dir: Path,
    ) -> None:
        self.db_path = db_path.expanduser().resolve()
        self.scenario_dir = scenario_dir.expanduser().resolve()
        self.report_dir = report_dir.expanduser().resolve()
        self.selected_target = DEFAULT_TARGETS[0]["name"]

    def list_targets(self) -> Dict[str, Any]:
        return {
            "selected_target": self.selected_target,
            "targets": DEFAULT_TARGETS,
        }

    def select_target(self, name: str) -> Dict[str, Any]:
        names = {target["name"] for target in DEFAULT_TARGETS}
        if name not in names:
            raise ValueError("Unknown target: {}".format(name))
        self.selected_target = name
        return self.list_targets()

    def list_scenarios(self) -> List[Dict[str, Any]]:
        loaded = load_scenarios_from_directory(self.scenario_dir)
        rows: List[Dict[str, Any]] = []
        for item in loaded:
            scenario = item.scenario
            rows.append(
                {
                    "id": scenario.id,
                    "title": scenario.title,
                    "category": scenario.category,
                    "security_focus": scenario.security_focus,
                    "expected_behavior": [
                        {
                            "rule_id": expectation.rule_id,
                            "outcome": expectation.outcome,
                            "description": expectation.description,
                        }
                        for expectation in scenario.policy_expectations
                    ],
                    "scenario_path": item.scenario_path,
                }
            )
        return rows

    def list_runs(self) -> List[Dict[str, Any]]:
        storage = SQLiteStorage(self.db_path)
        try:
            rows = storage.runs.list_summaries()
        finally:
            storage.close()

        summaries: List[Dict[str, Any]] = []
        for row in rows:
            report_path = self.report_dir / "{}.md".format(row["run_id"])
            summaries.append(
                {
                    "run_id": row["run_id"],
                    "status": row["status"],
                    "scenario_id": row["scenario_id"],
                    "scenario_title": row.get("scenario_title") or row["scenario_id"],
                    "target": self.selected_target,
                    "timestamp": row["created_at"],
                    "verdict": row.get("verdict") or "pending",
                    "analysis_state": "ready" if row.get("verdict") else "pending",
                    "report_available": report_path.exists(),
                    "overall_score": row.get("overall_score"),
                }
            )
        return summaries

    def run_detail(self, run_id: str) -> Dict[str, Any]:
        storage = SQLiteStorage(self.db_path)
        try:
            bundle = storage.load_run_bundle(run_id)
            run_result = storage.reconstruct_run_result(run_id)
        finally:
            storage.close()

        scenario = bundle["scenario"]
        events = bundle["events"]
        tool_calls = [
            {
                "tool": event_payload.get("tool_name"),
                "arguments": event_payload.get("arguments", {}),
                "step_index": event["step_index"],
                "timestamp": event["timestamp"],
            }
            for event in events
            if event["event_type"] == "tool_call_requested"
            for event_payload in [json.loads(event["payload_json"])]
        ]

        violations = [
            {
                "rule_id": violation["rule_id"],
                "severity": violation["severity"],
                "action": violation["action"],
                "message": violation["message"],
            }
            for violation in bundle["violations"]
        ]

        event_rows = [
            {
                "step_index": event["step_index"],
                "timestamp": event["timestamp"],
                "event_type": event["event_type"],
                "payload": json.loads(event["payload_json"]),
            }
            for event in events
        ]

        return {
            "run_id": run_id,
            "status": run_result.status.value,
            "scenario": {
                "id": scenario["id"] if scenario else run_result.scenario_id,
                "title": scenario["title"] if scenario else run_result.scenario_id,
                "category": scenario["category"] if scenario else "unknown",
            },
            "trace": event_rows,
            "tool_calls": tool_calls,
            "violations": violations,
            "evaluation": run_result.evaluation.model_dump(mode="json")
            if run_result.evaluation
            else None,
            "final_response": run_result.final_response,
        }

    def run_execute(
        self,
        *,
        scenario_id: str,
        target: Optional[str] = None,
        max_steps: int = 8,
    ) -> Dict[str, Any]:
        selected_target = target or self.selected_target
        self.select_target(selected_target)

        loaded = self._load_scenario_by_id(scenario_id)
        run_id = "ui-{}-{}".format(scenario_id.lower(), uuid4().hex[:6])

        runner = AgentRunner(
            adapter=DeterministicUiAdapter(),
            tool_registry=create_default_tool_registry(),
            max_steps=max_steps,
        )
        run_result = runner.run(loaded, run_id=run_id)

        storage = SQLiteStorage(self.db_path)
        try:
            storage.persist_full_run(loaded, run_result)
        finally:
            storage.close()

        report_path = MarkdownReportGenerator().generate(
            run_result,
            loaded,
            self.report_dir,
        )

        return {
            "run_id": run_result.run_id,
            "scenario_id": run_result.scenario_id,
            "status": run_result.status.value,
            "verdict": run_result.evaluation.verdict.value if run_result.evaluation else "n/a",
            "overall_score": run_result.evaluation.scores.overall_score
            if run_result.evaluation
            else None,
            "report_path": str(report_path),
        }

    def report_markdown(self, run_id: str) -> str:
        report_path = self.report_dir / "{}.md".format(run_id)
        if report_path.exists():
            return report_path.read_text(encoding="utf-8")

        storage = SQLiteStorage(self.db_path)
        try:
            regenerated = storage.regenerate_report(run_id, self.report_dir)
        finally:
            storage.close()
        return regenerated.read_text(encoding="utf-8")

    def _load_scenario_by_id(self, scenario_id: str):
        loaded = load_scenarios_from_directory(self.scenario_dir)
        for item in loaded:
            if item.scenario.id == scenario_id:
                return item
        raise ValueError("Scenario not found: {}".format(scenario_id))


@dataclass
class UiServerConfig:
    host: str
    port: int
    db_path: Path
    scenario_dir: Path
    report_dir: Path
    ui_dir: Path


def run_ui_server(config: UiServerConfig) -> None:
    service = UiDataService(
        db_path=config.db_path,
        scenario_dir=config.scenario_dir,
        report_dir=config.report_dir,
    )

    handler_cls = _build_handler(service=service, ui_dir=config.ui_dir)
    server = ThreadingHTTPServer((config.host, config.port), handler_cls)

    print(
        "ui_server=http://{}:{}/ db={} scenarios={} reports={}".format(
            config.host,
            config.port,
            config.db_path,
            config.scenario_dir,
            config.report_dir,
        )
    )

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


def _build_handler(*, service: UiDataService, ui_dir: Path):
    class UiHandler(SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=str(ui_dir), **kwargs)

        def do_GET(self):
            parsed = urlparse(self.path)
            path = parsed.path

            try:
                if path == "/api/health":
                    return self._send_json({"ok": True})
                if path == "/api/targets":
                    return self._send_json(service.list_targets())
                if path == "/api/scenarios":
                    return self._send_json({"scenarios": service.list_scenarios()})
                if path == "/api/runs":
                    return self._send_json({"runs": service.list_runs()})
                if path.startswith("/api/runs/"):
                    run_id = path.split("/")[-1]
                    return self._send_json(service.run_detail(run_id))
                if path.startswith("/api/reports/") and path.endswith("/download"):
                    run_id = path.split("/")[-2]
                    markdown = service.report_markdown(run_id)
                    return self._send_markdown(markdown, run_id=run_id, download=True)
                if path.startswith("/api/reports/"):
                    run_id = path.split("/")[-1]
                    markdown = service.report_markdown(run_id)
                    return self._send_markdown(markdown, run_id=run_id, download=False)
            except Exception as exc:
                return self._send_json(
                    {"error": str(exc)},
                    status=HTTPStatus.BAD_REQUEST,
                )

            return super().do_GET()

        def do_POST(self):
            parsed = urlparse(self.path)
            path = parsed.path

            content_length = int(self.headers.get("Content-Length", 0))
            body_bytes = self.rfile.read(content_length) if content_length > 0 else b"{}"
            try:
                body = json.loads(body_bytes.decode("utf-8"))
            except json.JSONDecodeError:
                body = {}

            try:
                if path == "/api/targets/select":
                    selected = service.select_target(str(body.get("name", "")))
                    return self._send_json(selected)
                if path == "/api/runs/execute":
                    scenario_id = str(body.get("scenario_id", ""))
                    target = body.get("target")
                    max_steps = int(body.get("max_steps", 8))
                    result = service.run_execute(
                        scenario_id=scenario_id,
                        target=target,
                        max_steps=max_steps,
                    )
                    return self._send_json(result)
            except Exception as exc:
                return self._send_json(
                    {"error": str(exc)},
                    status=HTTPStatus.BAD_REQUEST,
                )

            return self._send_json(
                {"error": "Unknown endpoint"},
                status=HTTPStatus.NOT_FOUND,
            )

        def _send_json(self, payload: Dict[str, Any], status: HTTPStatus = HTTPStatus.OK):
            data = json.dumps(payload, sort_keys=True).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def _send_markdown(self, markdown: str, *, run_id: str, download: bool):
            data = markdown.encode("utf-8")
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", "text/markdown; charset=utf-8")
            if download:
                self.send_header(
                    "Content-Disposition",
                    'attachment; filename="{}.md"'.format(run_id),
                )
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

    return UiHandler
