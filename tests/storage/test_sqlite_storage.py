from __future__ import annotations

from pathlib import Path

from act0r.adapters import AdapterRequest, AdapterResponse, AgentAdapter
from act0r.runner import AgentRunner
from act0r.scenarios import load_scenario
from act0r.storage import SQLiteStorage
from act0r.tools import create_default_tool_registry


class FinalAdapter(AgentAdapter):
    def generate(self, request: AdapterRequest) -> AdapterResponse:
        return AdapterResponse(
            assistant_text="Summary prepared for persistence test.",
            tool_calls=[],
            is_final=True,
        )


def _build_run(run_id: str):
    scenario = load_scenario("scenarios/mvp/SCN-001_benign_email_summary.yaml")
    runner = AgentRunner(
        adapter=FinalAdapter(),
        tool_registry=create_default_tool_registry(),
        max_steps=3,
    )
    run_result = runner.run(scenario, run_id=run_id)
    return scenario, run_result


def test_sqlite_storage_persist_and_reconstruct_flow(tmp_path: Path) -> None:
    db_path = tmp_path / "act0r.sqlite"
    storage = SQLiteStorage(db_path)

    loaded_scenario, run_result = _build_run("persist-run-001")
    storage.persist_full_run(loaded_scenario, run_result)

    bundle = storage.load_run_bundle("persist-run-001")
    assert bundle["run"]["run_id"] == "persist-run-001"
    assert bundle["scenario"]["id"] == loaded_scenario.scenario.id
    assert len(bundle["events"]) > 0
    assert bundle["scores"]["verdict"] == run_result.evaluation.verdict.value

    reconstructed = storage.reconstruct_run_result("persist-run-001")
    assert reconstructed.run_id == run_result.run_id
    assert reconstructed.status == run_result.status
    assert reconstructed.evaluation.verdict == run_result.evaluation.verdict

    storage.close()


def test_sqlite_storage_regenerates_report_from_persisted_data(tmp_path: Path) -> None:
    db_path = tmp_path / "act0r.sqlite"
    report_dir = tmp_path / "reports"
    storage = SQLiteStorage(db_path)

    loaded_scenario, run_result = _build_run("persist-run-002")
    storage.persist_full_run(loaded_scenario, run_result)

    report_path = storage.regenerate_report("persist-run-002", report_dir)

    assert report_path.exists()
    assert report_path.name == "persist-run-002.md"
    assert "# act0r Run Report" in report_path.read_text(encoding="utf-8")

    storage.close()
