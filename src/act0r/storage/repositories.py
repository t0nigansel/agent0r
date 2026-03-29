from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

from act0r.evaluation import RunEvaluation
from act0r.runner import RunResult
from act0r.scenarios.models import LoadedScenario
from act0r.trace import EventType, RunTrace


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class ScenarioRepository:
    def __init__(self, connection: sqlite3.Connection) -> None:
        self.connection = connection

    def save(self, loaded_scenario: LoadedScenario) -> None:
        scenario = loaded_scenario.scenario
        source_path = Path(loaded_scenario.scenario_path)
        raw_yaml = source_path.read_text(encoding="utf-8")

        self.connection.execute(
            """
            INSERT INTO scenarios (id, title, category, source_path, raw_yaml, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                title=excluded.title,
                category=excluded.category,
                source_path=excluded.source_path,
                raw_yaml=excluded.raw_yaml
            """,
            (
                scenario.id,
                scenario.title,
                scenario.category,
                str(source_path),
                raw_yaml,
                _utc_now_iso(),
            ),
        )

    def get(self, scenario_id: str) -> Optional[Dict]:
        row = self.connection.execute(
            "SELECT * FROM scenarios WHERE id = ?",
            (scenario_id,),
        ).fetchone()
        return dict(row) if row else None


class RunRepository:
    def __init__(self, connection: sqlite3.Connection) -> None:
        self.connection = connection

    def save(self, run_result: RunResult) -> None:
        verdict = run_result.evaluation.verdict.value if run_result.evaluation else None
        overall_score = (
            run_result.evaluation.scores.overall_score if run_result.evaluation else None
        )

        self.connection.execute(
            """
            INSERT INTO runs (
                run_id,
                scenario_id,
                status,
                steps_executed,
                final_response,
                verdict,
                overall_score,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(run_id) DO UPDATE SET
                scenario_id=excluded.scenario_id,
                status=excluded.status,
                steps_executed=excluded.steps_executed,
                final_response=excluded.final_response,
                verdict=excluded.verdict,
                overall_score=excluded.overall_score
            """,
            (
                run_result.run_id,
                run_result.scenario_id,
                run_result.status.value,
                run_result.steps_executed,
                run_result.final_response,
                verdict,
                overall_score,
                _utc_now_iso(),
            ),
        )

    def get(self, run_id: str) -> Optional[Dict]:
        row = self.connection.execute(
            "SELECT * FROM runs WHERE run_id = ?",
            (run_id,),
        ).fetchone()
        return dict(row) if row else None


class EventRepository:
    def __init__(self, connection: sqlite3.Connection) -> None:
        self.connection = connection

    def save_trace(self, run_id: str, trace: RunTrace) -> None:
        self.connection.execute("DELETE FROM events WHERE run_id = ?", (run_id,))

        for event in trace.events:
            self.connection.execute(
                """
                INSERT INTO events (run_id, step_index, timestamp, event_type, payload_json)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    run_id,
                    event.step_index,
                    event.timestamp.isoformat(),
                    event.event_type.value,
                    json.dumps(event.payload, sort_keys=True),
                ),
            )

    def list_by_run(self, run_id: str) -> List[Dict]:
        rows = self.connection.execute(
            "SELECT * FROM events WHERE run_id = ? ORDER BY step_index ASC",
            (run_id,),
        ).fetchall()
        return [dict(row) for row in rows]


class ViolationRepository:
    def __init__(self, connection: sqlite3.Connection) -> None:
        self.connection = connection

    def save_from_trace(self, run_id: str, trace: RunTrace) -> None:
        self.connection.execute("DELETE FROM violations WHERE run_id = ?", (run_id,))

        for event in trace.events:
            if event.event_type != EventType.VIOLATION_DETECTED:
                continue
            payload = event.payload
            self.connection.execute(
                """
                INSERT INTO violations (run_id, rule_id, severity, action, message, evidence_json)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    run_id,
                    payload.get("rule_id", "unknown"),
                    payload.get("severity", "unknown"),
                    payload.get("action", "unknown"),
                    payload.get("message", ""),
                    json.dumps(payload.get("evidence_event_indexes", []), sort_keys=True),
                ),
            )

    def list_by_run(self, run_id: str) -> List[Dict]:
        rows = self.connection.execute(
            "SELECT * FROM violations WHERE run_id = ? ORDER BY id ASC",
            (run_id,),
        ).fetchall()
        return [dict(row) for row in rows]


class ScoreRepository:
    def __init__(self, connection: sqlite3.Connection) -> None:
        self.connection = connection

    def save(self, run_id: str, evaluation: RunEvaluation) -> None:
        scores = evaluation.scores
        self.connection.execute(
            """
            INSERT INTO scores (
                run_id,
                verdict,
                goal_alignment,
                tool_safety,
                memory_safety,
                data_exfiltration_resistance,
                prompt_injection_resistance,
                overall_score,
                critical_failures_json,
                notes_json
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(run_id) DO UPDATE SET
                verdict=excluded.verdict,
                goal_alignment=excluded.goal_alignment,
                tool_safety=excluded.tool_safety,
                memory_safety=excluded.memory_safety,
                data_exfiltration_resistance=excluded.data_exfiltration_resistance,
                prompt_injection_resistance=excluded.prompt_injection_resistance,
                overall_score=excluded.overall_score,
                critical_failures_json=excluded.critical_failures_json,
                notes_json=excluded.notes_json
            """,
            (
                run_id,
                evaluation.verdict.value,
                scores.goal_alignment,
                scores.tool_safety,
                scores.memory_safety,
                scores.data_exfiltration_resistance,
                scores.prompt_injection_resistance,
                scores.overall_score,
                json.dumps(evaluation.critical_failures, sort_keys=True),
                json.dumps(evaluation.notes, sort_keys=True),
            ),
        )

    def get(self, run_id: str) -> Optional[Dict]:
        row = self.connection.execute(
            "SELECT * FROM scores WHERE run_id = ?",
            (run_id,),
        ).fetchone()
        return dict(row) if row else None
