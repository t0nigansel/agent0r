from __future__ import annotations

import json
from pathlib import Path
from typing import Union

import yaml
from pydantic import ValidationError

from .errors import ScenarioLoadError
from .models import FixtureReference, LoadedFixture, LoadedScenario, Scenario


def load_scenario(scenario_path: Union[str, Path]) -> LoadedScenario:
    path = Path(scenario_path).expanduser().resolve()

    if not path.exists():
        raise ScenarioLoadError(path, "Scenario file does not exist")

    try:
        raw_content = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise ScenarioLoadError(path, "Scenario file could not be read", details=[str(exc)]) from exc

    try:
        parsed = yaml.safe_load(raw_content)
    except yaml.YAMLError as exc:
        raise ScenarioLoadError(path, "Scenario YAML parsing failed", details=[str(exc)]) from exc

    if parsed is None:
        parsed = {}
    if not isinstance(parsed, dict):
        raise ScenarioLoadError(path, "Scenario YAML root must be a mapping")

    try:
        scenario = Scenario.model_validate(parsed)
    except ValidationError as exc:
        raise ScenarioLoadError(
            path,
            "Scenario validation failed",
            details=_format_validation_errors(exc),
        ) from exc

    fixtures = _load_fixtures(path.parent, scenario.fixtures, scenario_path=path)

    return LoadedScenario(
        scenario_path=str(path),
        scenario=scenario,
        fixtures=fixtures,
    )


def load_scenarios_from_directory(directory: Union[str, Path]) -> list[LoadedScenario]:
    base_dir = Path(directory).expanduser().resolve()
    if not base_dir.exists() or not base_dir.is_dir():
        raise ScenarioLoadError(base_dir, "Scenario directory does not exist or is not a directory")

    scenario_files = sorted(list(base_dir.glob("*.yml")) + list(base_dir.glob("*.yaml")))
    return [load_scenario(path) for path in scenario_files]


def _load_fixtures(
    scenario_dir: Path,
    fixture_refs: dict[str, FixtureReference],
    *,
    scenario_path: Path,
) -> dict[str, LoadedFixture]:
    loaded: dict[str, LoadedFixture] = {}

    for fixture_name in sorted(fixture_refs):
        fixture_ref = fixture_refs[fixture_name]
        fixture_path = _resolve_fixture_path(scenario_dir, fixture_ref.path)

        if not fixture_path.exists():
            if fixture_ref.required:
                raise ScenarioLoadError(
                    scenario_path,
                    f"Required fixture '{fixture_name}' was not found",
                    details=[f"resolved path: {fixture_path}"],
                )
            fixture_content = None
        else:
            fixture_content = _read_fixture_content(
                fixture_name,
                fixture_path,
                fixture_ref,
                scenario_path=scenario_path,
            )

        loaded[fixture_name] = LoadedFixture(
            name=fixture_name,
            source_path=str(fixture_path),
            format=fixture_ref.format,
            trusted=fixture_ref.trusted,
            content=fixture_content,
        )

    return loaded


def _resolve_fixture_path(scenario_dir: Path, fixture_path: str) -> Path:
    candidate = Path(fixture_path).expanduser()
    if not candidate.is_absolute():
        candidate = scenario_dir / candidate
    return candidate.resolve()


def _read_fixture_content(
    fixture_name: str,
    fixture_path: Path,
    fixture_ref: FixtureReference,
    *,
    scenario_path: Path,
):
    try:
        raw = fixture_path.read_text(encoding="utf-8")
    except OSError as exc:
        raise ScenarioLoadError(
            scenario_path,
            f"Fixture '{fixture_name}' could not be read",
            details=[str(exc)],
        ) from exc

    if fixture_ref.format == "text":
        return raw

    if fixture_ref.format == "json":
        try:
            return json.loads(raw)
        except json.JSONDecodeError as exc:
            raise ScenarioLoadError(
                scenario_path,
                f"Fixture '{fixture_name}' JSON decoding failed",
                details=[str(exc)],
            ) from exc

    if fixture_ref.format == "yaml":
        try:
            return yaml.safe_load(raw)
        except yaml.YAMLError as exc:
            raise ScenarioLoadError(
                scenario_path,
                f"Fixture '{fixture_name}' YAML decoding failed",
                details=[str(exc)],
            ) from exc

    raise ScenarioLoadError(
        scenario_path,
        f"Fixture '{fixture_name}' uses unsupported format '{fixture_ref.format}'",
    )


def _format_validation_errors(exc: ValidationError) -> list[str]:
    formatted: list[str] = []
    for error in exc.errors():
        location_parts = [str(part) for part in error.get("loc", ())]
        location = ".".join(location_parts) if location_parts else "<root>"
        message = error.get("msg", "Invalid value")
        formatted.append(f"{location}: {message}")
    return formatted
