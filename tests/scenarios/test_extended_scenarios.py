from __future__ import annotations

from pathlib import Path

from act0r.scenarios import load_scenario, load_scenarios_from_directory

EXTENDED_SCENARIO_DIR = Path(__file__).resolve().parents[2] / "scenarios" / "extended"


def test_extended_scenario_pack_contains_expected_ids() -> None:
    loaded = load_scenarios_from_directory(EXTENDED_SCENARIO_DIR)

    assert [item.scenario.id for item in loaded] == [
        "SCN-101",
        "SCN-102",
        "SCN-103",
    ]


def test_each_extended_scenario_uses_untrusted_fixture_and_policy_expectation() -> None:
    for path in sorted(EXTENDED_SCENARIO_DIR.glob("*.yaml")):
        loaded = load_scenario(path)

        assert loaded.scenario.security_focus
        assert loaded.scenario.policy_expectations
        assert any(not fixture.trusted for fixture in loaded.fixtures.values())
