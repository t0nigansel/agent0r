from __future__ import annotations

from pathlib import Path

import pytest

from act0r.ui_backend import UiDataService



def test_ui_data_service_lists_targets_and_scenarios(tmp_path: Path) -> None:
    service = UiDataService(
        db_path=tmp_path / "act0r.sqlite",
        scenario_dir=Path("scenarios/mvp"),
        report_dir=tmp_path / "reports",
    )

    targets = service.list_targets()
    scenarios = service.list_scenarios()

    assert targets["selected_target"] == "local-mock"
    assert len(targets["targets"]) >= 2
    assert len(scenarios) >= 6
    assert scenarios[0]["id"].startswith("SCN-")



def test_ui_data_service_execute_run_and_read_detail(tmp_path: Path) -> None:
    service = UiDataService(
        db_path=tmp_path / "act0r.sqlite",
        scenario_dir=Path("scenarios/mvp"),
        report_dir=tmp_path / "reports",
    )

    executed = service.run_execute(scenario_id="SCN-001", target="local-mock", max_steps=4)
    run_id = executed["run_id"]

    runs = service.list_runs()
    assert any(item["run_id"] == run_id for item in runs)

    detail = service.run_detail(run_id)
    assert detail["run_id"] == run_id
    assert detail["scenario"]["id"] == "SCN-001"
    assert detail["evaluation"] is not None
    assert len(detail["trace"]) > 0

    report_markdown = service.report_markdown(run_id)
    assert "# act0r Run Report" in report_markdown



def test_ui_data_service_rejects_unknown_scenario(tmp_path: Path) -> None:
    service = UiDataService(
        db_path=tmp_path / "act0r.sqlite",
        scenario_dir=Path("scenarios/mvp"),
        report_dir=tmp_path / "reports",
    )

    with pytest.raises(ValueError):
        service.run_execute(scenario_id="SCN-404", target="local-mock")


def test_ui_data_service_compares_runs_deterministically(tmp_path: Path) -> None:
    service = UiDataService(
        db_path=tmp_path / "act0r.sqlite",
        scenario_dir=Path("scenarios/mvp"),
        report_dir=tmp_path / "reports",
    )

    left = service.run_execute(scenario_id="SCN-001", target="local-mock", max_steps=4)
    right = service.run_execute(scenario_id="SCN-005", target="local-mock", max_steps=4)

    comparison = service.compare_runs(left["run_id"], right["run_id"])

    assert comparison["left"]["run_id"] == left["run_id"]
    assert comparison["right"]["run_id"] == right["run_id"]
    assert comparison["left"]["scenario_id"] == "SCN-001"
    assert comparison["right"]["scenario_id"] == "SCN-005"
    assert comparison["left"]["verdict"] == "PASS"
    assert comparison["right"]["verdict"] == "CRITICAL_FAIL"
    assert comparison["delta"]["overall_score"] is not None
    assert comparison["delta"]["overall_score"] < 0
    assert comparison["delta"]["violation_count"] > 0
    assert "P-001" in comparison["violations"]["new_in_right"]
    assert "export_data" in comparison["tools"]["new_in_right"]
