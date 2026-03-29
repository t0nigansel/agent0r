from __future__ import annotations

from pathlib import Path

from act0r.scenarios import load_scenario, load_scenarios_from_directory

MVP_SCENARIO_DIR = Path(__file__).resolve().parents[2] / "scenarios" / "mvp"


def test_mvp_scenario_pack_contains_expected_ids() -> None:
    loaded = load_scenarios_from_directory(MVP_SCENARIO_DIR)

    assert [item.scenario.id for item in loaded] == [
        "SCN-001",
        "SCN-002",
        "SCN-003",
        "SCN-004",
        "SCN-005",
        "SCN-006",
    ]


def test_each_mvp_scenario_has_policy_expectations_and_focus() -> None:
    for path in sorted(MVP_SCENARIO_DIR.glob("*.yaml")):
        loaded = load_scenario(path)
        assert loaded.scenario.security_focus
        assert loaded.scenario.policy_expectations
        assert loaded.fixtures
