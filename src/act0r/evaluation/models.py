from __future__ import annotations

from enum import Enum
from typing import List

from pydantic import BaseModel, ConfigDict, Field


class VerdictClass(str, Enum):
    PASS = "PASS"
    PASS_WITH_WARNINGS = "PASS_WITH_WARNINGS"
    FAIL = "FAIL"
    CRITICAL_FAIL = "CRITICAL_FAIL"


class EvaluationScores(BaseModel):
    model_config = ConfigDict(extra="forbid")

    goal_alignment: int = Field(ge=0, le=100)
    tool_safety: int = Field(ge=0, le=100)
    memory_safety: int = Field(ge=0, le=100)
    data_exfiltration_resistance: int = Field(ge=0, le=100)
    prompt_injection_resistance: int = Field(ge=0, le=100)
    overall_score: int = Field(ge=0, le=100)


class RunEvaluation(BaseModel):
    model_config = ConfigDict(extra="forbid")

    verdict: VerdictClass
    scores: EvaluationScores
    violation_count: int = Field(ge=0)
    critical_failures: List[str] = Field(default_factory=list)
    notes: List[str] = Field(default_factory=list)
