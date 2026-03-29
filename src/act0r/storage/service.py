from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Optional

from act0r.evaluation import DeterministicEvaluator, EvaluationScores, RunEvaluation, VerdictClass
from act0r.reporting import MarkdownReportGenerator
from act0r.runner import RunResult, RunStatus
from act0r.scenarios import load_scenario
from act0r.scenarios.models import LoadedScenario
from act0r.trace import EventType, RunTrace, TraceEvent

from .db import initialize_database
from .repositories import (
    EventRepository,
    RunRepository,
    ScenarioRepository,
    ScoreRepository,
    ViolationRepository,
)


class SQLiteStorage:
    def __init__(self, db_path: Path) -> None:
        self.connection = initialize_database(db_path)
        self.scenarios = ScenarioRepository(self.connection)
        self.runs = RunRepository(self.connection)
        self.events = EventRepository(self.connection)
        self.violations = ViolationRepository(self.connection)
        self.scores = ScoreRepository(self.connection)

    def close(self) -> None:
        self.connection.close()

    def persist_full_run(self, loaded_scenario: LoadedScenario, run_result: RunResult) -> None:
        self.scenarios.save(loaded_scenario)
        self.runs.save(run_result)
        self.events.save_trace(run_result.run_id, run_result.trace)
        self.violations.save_from_trace(run_result.run_id, run_result.trace)
        if run_result.evaluation:
            self.scores.save(run_result.run_id, run_result.evaluation)
        self.connection.commit()

    def load_run_bundle(self, run_id: str) -> Dict:
        run_record = self.runs.get(run_id)
        if run_record is None:
            raise ValueError("Run not found: {}".format(run_id))

        scenario_record = self.scenarios.get(run_record["scenario_id"])
        event_records = self.events.list_by_run(run_id)
        violation_records = self.violations.list_by_run(run_id)
        score_record = self.scores.get(run_id)

        return {
            "run": run_record,
            "scenario": scenario_record,
            "events": event_records,
            "violations": violation_records,
            "scores": score_record,
        }

    def reconstruct_run_result(self, run_id: str) -> RunResult:
        bundle = self.load_run_bundle(run_id)
        run_record = bundle["run"]
        events = bundle["events"]
        score_record = bundle["scores"]
        violations = bundle["violations"]

        trace_events = [
            TraceEvent(
                step_index=event["step_index"],
                timestamp=_parse_datetime(event["timestamp"]),
                event_type=EventType(event["event_type"]),
                payload=json.loads(event["payload_json"]),
            )
            for event in events
        ]

        if trace_events:
            started_at = trace_events[0].timestamp
        else:
            started_at = _parse_datetime(run_record["created_at"])

        trace = RunTrace(run_id=run_id, started_at=started_at, events=trace_events)
        evaluation = _evaluation_from_score_record(score_record, len(violations))
        if evaluation is None:
            evaluation = DeterministicEvaluator().evaluate(trace)

        return RunResult(
            run_id=run_record["run_id"],
            scenario_id=run_record["scenario_id"],
            status=RunStatus(run_record["status"]),
            steps_executed=run_record["steps_executed"],
            trace=trace,
            evaluation=evaluation,
            final_response=run_record["final_response"],
        )

    def regenerate_report(self, run_id: str, output_dir: Path) -> Path:
        bundle = self.load_run_bundle(run_id)
        scenario_record = bundle["scenario"]
        if scenario_record is None:
            raise ValueError("Scenario record missing for run: {}".format(run_id))

        loaded_scenario = load_scenario(scenario_record["source_path"])
        run_result = self.reconstruct_run_result(run_id)

        generator = MarkdownReportGenerator()
        return generator.generate(run_result, loaded_scenario, output_dir)


def _evaluation_from_score_record(score_record: Optional[Dict], violation_count: int) -> Optional[RunEvaluation]:
    if score_record is None:
        return None

    return RunEvaluation(
        verdict=VerdictClass(score_record["verdict"]),
        scores=EvaluationScores(
            goal_alignment=score_record["goal_alignment"],
            tool_safety=score_record["tool_safety"],
            memory_safety=score_record["memory_safety"],
            data_exfiltration_resistance=score_record["data_exfiltration_resistance"],
            prompt_injection_resistance=score_record["prompt_injection_resistance"],
            overall_score=score_record["overall_score"],
        ),
        violation_count=violation_count,
        critical_failures=json.loads(score_record["critical_failures_json"]),
        notes=json.loads(score_record["notes_json"]),
    )


def _parse_datetime(value: str) -> datetime:
    parsed = datetime.fromisoformat(value)
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)
