from __future__ import annotations

from pathlib import Path

import pytest

from act0r.scenarios import ScenarioLoadError, load_scenario, load_scenarios_from_directory

FIXTURE_ROOT = Path(__file__).resolve().parents[1] / "fixtures"
SCENARIOS_DIR = FIXTURE_ROOT / "scenarios"


def test_load_scenario_with_fixture_resolution() -> None:
    loaded = load_scenario(SCENARIOS_DIR / "valid_scenario.yaml")

    assert loaded.scenario.id == "SCN-001"
    assert loaded.scenario.title == "Benign email summary"
    assert sorted(loaded.fixtures.keys()) == ["inbox_email", "metadata", "policy"]

    assert "summarize this email" in loaded.fixtures["inbox_email"].content.lower()
    assert loaded.fixtures["metadata"].content["source"] == "mailbox"
    assert loaded.fixtures["policy"].content["mode"] == "strict"


def test_missing_required_fields_raise_readable_error() -> None:
    with pytest.raises(ScenarioLoadError) as exc_info:
        load_scenario(SCENARIOS_DIR / "invalid_missing_user_task.yaml")

    message = str(exc_info.value)
    assert "Scenario validation failed" in message
    assert "user_task" in message


def test_missing_required_fixture_raises_readable_error() -> None:
    with pytest.raises(ScenarioLoadError) as exc_info:
        load_scenario(SCENARIOS_DIR / "invalid_missing_fixture.yaml")

    message = str(exc_info.value)
    assert "Required fixture 'inbox_email' was not found" in message
    assert "resolved path" in message


def test_optional_missing_fixture_returns_none_content() -> None:
    loaded = load_scenario(SCENARIOS_DIR / "valid_optional_missing_fixture.yaml")

    assert loaded.fixtures["maybe_present"].content is None


def test_directory_loading_is_deterministic(tmp_path: Path) -> None:
    (tmp_path / "zeta.yaml").write_text(
        "\n".join(
            [
                "id: SCN-011",
                "title: Zeta",
                "system_prompt: You are careful.",
                "user_task: Do task.",
            ]
        ),
        encoding="utf-8",
    )
    (tmp_path / "alpha.yml").write_text(
        "\n".join(
            [
                "id: SCN-010",
                "title: Alpha",
                "system_prompt: You are careful.",
                "user_task: Do task.",
            ]
        ),
        encoding="utf-8",
    )

    loaded = load_scenarios_from_directory(tmp_path)

    assert [entry.scenario.id for entry in loaded] == ["SCN-010", "SCN-011"]
