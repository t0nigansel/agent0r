from __future__ import annotations

import json
import zipfile
from pathlib import Path

from act0r.adapters import AdapterRequest, AdapterResponse, AgentAdapter
from act0r.reporting import MarkdownReportGenerator, RunArtifactExporter
from act0r.runner import AgentRunner
from act0r.scenarios import load_scenario
from act0r.tools import create_default_tool_registry


class FinalAdapter(AgentAdapter):
    def generate(self, request: AdapterRequest) -> AdapterResponse:
        return AdapterResponse(
            assistant_text="Summary prepared for artifact export test.",
            tool_calls=[],
            is_final=True,
        )


def _run_result(run_id: str):
    scenario = load_scenario("scenarios/mvp/SCN-001_benign_email_summary.yaml")
    runner = AgentRunner(
        adapter=FinalAdapter(),
        tool_registry=create_default_tool_registry(),
        max_steps=3,
    )
    result = runner.run(scenario, run_id=run_id)
    return scenario, result


def test_run_artifact_exporter_generates_json_pdf_and_bundle(tmp_path: Path) -> None:
    loaded_scenario, run_result = _run_result("artifact-export-run")

    markdown_path = MarkdownReportGenerator().generate(run_result, loaded_scenario, tmp_path)
    markdown_text = markdown_path.read_text(encoding="utf-8")

    exporter = RunArtifactExporter()
    json_path = exporter.generate_json(run_result, loaded_scenario, tmp_path)
    pdf_path = exporter.generate_pdf(
        run_result,
        loaded_scenario,
        tmp_path,
        markdown_text=markdown_text,
    )
    bundle_path = exporter.generate_bundle(
        run_id=run_result.run_id,
        output_dir=tmp_path,
        artifact_paths={
            "markdown": markdown_path,
            "json": json_path,
            "pdf": pdf_path,
        },
    )

    payload = json.loads(json_path.read_text(encoding="utf-8"))
    assert payload["run"]["run_id"] == "artifact-export-run"
    assert payload["scenario"]["scenario"]["id"] == "SCN-001"

    assert pdf_path.read_bytes().startswith(b"%PDF-1.4")

    with zipfile.ZipFile(bundle_path, "r") as archive:
        names = sorted(archive.namelist())

    assert names == [
        "artifact-export-run.json",
        "artifact-export-run.md",
        "artifact-export-run.pdf",
        "manifest.json",
    ]
