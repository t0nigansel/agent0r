from __future__ import annotations

from typing import Any, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

SCENARIO_ID_PATTERN = r"^SCN-\d{3}$"


class FixtureReference(BaseModel):
    model_config = ConfigDict(extra="forbid")

    path: str = Field(min_length=1)
    format: Literal["text", "json", "yaml"] = "text"
    trusted: bool = False
    required: bool = True
    description: Optional[str] = None

    @field_validator("path")
    @classmethod
    def validate_path(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("Fixture path must not be empty.")
        return normalized


class ScenarioTool(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1)
    risk_level: Literal["low", "medium", "high"] = "low"
    side_effects: bool = False
    requires_confirmation: bool = False


class PolicyExpectation(BaseModel):
    model_config = ConfigDict(extra="forbid")

    rule_id: str = Field(min_length=1)
    description: str = Field(min_length=1)
    outcome: Literal["allow", "deny", "warn", "block"]


class Scenario(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str = Field(pattern=SCENARIO_ID_PATTERN)
    title: str = Field(min_length=1)
    system_prompt: str = Field(min_length=1)
    user_task: str = Field(min_length=1)

    description: Optional[str] = None
    category: str = "general"
    security_focus: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    tools: list[ScenarioTool] = Field(default_factory=list)
    fixtures: dict[str, FixtureReference] = Field(default_factory=dict)
    policy_expectations: list[PolicyExpectation] = Field(default_factory=list)

    @field_validator("fixtures", mode="before")
    @classmethod
    def normalize_fixture_references(cls, value: Any) -> Any:
        if value is None:
            return {}
        if not isinstance(value, dict):
            raise TypeError("fixtures must be a mapping of names to fixture definitions")

        normalized: dict[str, Any] = {}
        for key, entry in value.items():
            if not isinstance(key, str) or not key.strip():
                raise TypeError("fixture names must be non-empty strings")
            if isinstance(entry, str):
                normalized[key] = {"path": entry}
            elif isinstance(entry, dict):
                normalized[key] = entry
            else:
                raise TypeError(
                    f"fixture '{key}' must be a string path or object definition"
                )
        return normalized

    @field_validator("security_focus", "tags")
    @classmethod
    def validate_string_lists(cls, values: list[str]) -> list[str]:
        cleaned: list[str] = []
        for value in values:
            normalized = value.strip()
            if not normalized:
                raise ValueError("List entries must not be empty strings.")
            cleaned.append(normalized)
        return cleaned


class LoadedFixture(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    source_path: str
    format: Literal["text", "json", "yaml"]
    trusted: bool
    content: Optional[Any]


class LoadedScenario(BaseModel):
    model_config = ConfigDict(extra="forbid")

    scenario_path: str
    scenario: Scenario
    fixtures: dict[str, LoadedFixture] = Field(default_factory=dict)
