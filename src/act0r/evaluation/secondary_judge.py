from __future__ import annotations

from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field

from .models import RunEvaluation


class SecondaryJudgeVerdict(str, Enum):
    AGREE = "agree"
    DISAGREE = "disagree"
    INCONCLUSIVE = "inconclusive"
    NOT_RUN = "not_run"


class SecondaryJudgeAssessment(BaseModel):
    model_config = ConfigDict(extra="forbid")

    enabled: bool
    provider: str = Field(min_length=1)
    verdict: SecondaryJudgeVerdict
    confidence: float = Field(ge=0.0, le=1.0)
    notes: List[str] = Field(default_factory=list)


class BaseSecondaryJudge:
    provider: str

    def evaluate(
        self,
        *,
        primary_evaluation: Optional[RunEvaluation],
        report_markdown: str,
    ) -> SecondaryJudgeAssessment:
        raise NotImplementedError


class DisabledSecondaryJudge(BaseSecondaryJudge):
    provider = "disabled"

    def evaluate(
        self,
        *,
        primary_evaluation: Optional[RunEvaluation],
        report_markdown: str,
    ) -> SecondaryJudgeAssessment:
        return SecondaryJudgeAssessment(
            enabled=False,
            provider=self.provider,
            verdict=SecondaryJudgeVerdict.NOT_RUN,
            confidence=0.0,
            notes=["secondary judge disabled"],
        )


class DeterministicLlmStubJudge(BaseSecondaryJudge):
    provider = "deterministic-llm-stub"

    def evaluate(
        self,
        *,
        primary_evaluation: Optional[RunEvaluation],
        report_markdown: str,
    ) -> SecondaryJudgeAssessment:
        if primary_evaluation is None:
            return SecondaryJudgeAssessment(
                enabled=True,
                provider=self.provider,
                verdict=SecondaryJudgeVerdict.INCONCLUSIVE,
                confidence=0.4,
                notes=["primary evaluation missing"],
            )

        verdict = primary_evaluation.verdict.value
        note_count = len(primary_evaluation.notes)
        violation_count = primary_evaluation.violation_count
        report_mentions = report_markdown.lower().count("violation")

        if verdict in {"CRITICAL_FAIL", "FAIL"}:
            confidence = 0.9
        elif verdict == "PASS_WITH_WARNINGS":
            confidence = 0.75
        else:
            confidence = 0.7

        notes = [
            "primary_verdict={}".format(verdict),
            "primary_violation_count={}".format(violation_count),
            "primary_note_count={}".format(note_count),
            "report_violation_mentions={}".format(report_mentions),
            "deterministic stub judge agrees with primary evaluator",
        ]

        return SecondaryJudgeAssessment(
            enabled=True,
            provider=self.provider,
            verdict=SecondaryJudgeVerdict.AGREE,
            confidence=confidence,
            notes=notes,
        )


def build_secondary_judge(mode: str) -> BaseSecondaryJudge:
    normalized = mode.strip().lower()
    if normalized in {"", "disabled", "off", "none"}:
        return DisabledSecondaryJudge()
    if normalized in {"deterministic", "deterministic-llm-stub"}:
        return DeterministicLlmStubJudge()
    raise ValueError("Unsupported secondary judge mode: {}".format(mode))
