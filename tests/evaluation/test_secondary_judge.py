from __future__ import annotations

from act0r.evaluation import (
    SecondaryJudgeVerdict,
    VerdictClass,
    build_secondary_judge,
)
from act0r.evaluation.models import EvaluationScores, RunEvaluation


def _primary_evaluation(verdict: VerdictClass) -> RunEvaluation:
    return RunEvaluation(
        verdict=verdict,
        scores=EvaluationScores(
            goal_alignment=100,
            tool_safety=100,
            memory_safety=100,
            data_exfiltration_resistance=100,
            prompt_injection_resistance=100,
            overall_score=100,
        ),
        violation_count=0,
        critical_failures=[],
        notes=[],
    )


def test_secondary_judge_disabled_mode_returns_not_run() -> None:
    judge = build_secondary_judge("disabled")
    assessment = judge.evaluate(
        primary_evaluation=_primary_evaluation(VerdictClass.PASS),
        report_markdown="# report",
    )

    assert assessment.enabled is False
    assert assessment.verdict == SecondaryJudgeVerdict.NOT_RUN


def test_secondary_judge_deterministic_stub_agrees_with_primary() -> None:
    judge = build_secondary_judge("deterministic-llm-stub")
    assessment = judge.evaluate(
        primary_evaluation=_primary_evaluation(VerdictClass.PASS_WITH_WARNINGS),
        report_markdown="## Violations\nnone",
    )

    assert assessment.enabled is True
    assert assessment.provider == "deterministic-llm-stub"
    assert assessment.verdict == SecondaryJudgeVerdict.AGREE
    assert assessment.confidence >= 0.7
