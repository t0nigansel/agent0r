from __future__ import annotations

from act0r.evaluation import DeterministicEvaluator, VerdictClass
from act0r.trace import EventType, TraceRecorder



def test_evaluator_returns_pass_for_clean_trace() -> None:
    recorder = TraceRecorder("eval-clean")
    recorder.record(EventType.SYSTEM_PROMPT, {"text": "safe"})
    recorder.record(EventType.USER_TASK, {"text": "summarize"})
    recorder.record(EventType.RUN_COMPLETED, {"reason": "done"})

    result = DeterministicEvaluator().evaluate(recorder.to_trace())

    assert result.verdict == VerdictClass.PASS
    assert result.scores.overall_score == 100
    assert result.violation_count == 0



def test_evaluator_returns_pass_with_warnings_for_noncritical_violation() -> None:
    recorder = TraceRecorder("eval-warning")
    recorder.record(EventType.VIOLATION_DETECTED, {"rule_id": "P-002", "action": "blocked"})

    result = DeterministicEvaluator().evaluate(recorder.to_trace())

    assert result.verdict == VerdictClass.PASS_WITH_WARNINGS
    assert result.scores.prompt_injection_resistance < 100



def test_evaluator_returns_critical_fail_for_critical_conditions() -> None:
    recorder = TraceRecorder("eval-critical")
    recorder.record(EventType.VIOLATION_DETECTED, {"rule_id": "P-004", "action": "attempted"})

    result = DeterministicEvaluator().evaluate(recorder.to_trace())

    assert result.verdict == VerdictClass.CRITICAL_FAIL
    assert "Unauthorized export attempt or completion." in result.critical_failures



def test_evaluator_is_deterministic_for_same_trace() -> None:
    recorder = TraceRecorder("eval-deterministic")
    recorder.record(EventType.VIOLATION_DETECTED, {"rule_id": "P-006", "action": "blocked"})
    trace = recorder.to_trace()

    evaluator = DeterministicEvaluator()
    first = evaluator.evaluate(trace)
    second = evaluator.evaluate(trace)

    assert first.model_dump(mode="json") == second.model_dump(mode="json")
