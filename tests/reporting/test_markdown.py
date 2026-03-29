from __future__ import annotations

from pathlib import Path

from act0r.adapters import AdapterRequest, AdapterResponse, AgentAdapter
from act0r.reporting import MarkdownReportGenerator
from act0r.runner import AgentRunner
from act0r.scenarios import load_scenario
from act0r.tools import create_default_tool_registry


class FinalAdapter(AgentAdapter):
    def generate(self, request: AdapterRequest) -> AdapterResponse:
        return AdapterResponse(
            assistant_text="Summary prepared.",
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


def test_markdown_report_contains_required_sections() -> None:
    loaded_scenario, result = _run_result("report-sections")

    report = MarkdownReportGenerator().render(result, loaded_scenario)

    assert "## Run metadata" in report
    assert "## Scenario summary" in report
    assert "## Expected safe behavior" in report
    assert "## Observed behavior" in report
    assert "## Tool calls" in report
    assert "## Violations" in report
    assert "## Evaluation scores" in report
    assert "## Final assessment" in report
    assert "## Recommendations" in report


def test_markdown_report_generator_writes_one_file_per_run(tmp_path: Path) -> None:
    loaded_a, result_a = _run_result("report-run-a")
    loaded_b, result_b = _run_result("report-run-b")

    generator = MarkdownReportGenerator()
    path_a = generator.generate(result_a, loaded_a, tmp_path)
    path_b = generator.generate(result_b, loaded_b, tmp_path)

    assert path_a.exists()
    assert path_b.exists()
    assert path_a != path_b
    assert path_a.name == "report-run-a.md"
    assert path_b.name == "report-run-b.md"
    assert path_a.read_text(encoding="utf-8").startswith("# act0r Run Report")
