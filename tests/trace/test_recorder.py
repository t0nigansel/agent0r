from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from act0r.trace import EventType, TraceRecorder


def test_recorder_supports_all_required_event_types() -> None:
    recorder = TraceRecorder("run-001")

    event_types = [
        EventType.SYSTEM_PROMPT,
        EventType.USER_TASK,
        EventType.ASSISTANT_RESPONSE,
        EventType.TOOL_CALL_REQUESTED,
        EventType.TOOL_CALL_EXECUTED,
        EventType.TOOL_RESULT,
        EventType.POLICY_DECISION,
        EventType.VIOLATION_DETECTED,
        EventType.RUN_STOPPED,
        EventType.RUN_COMPLETED,
    ]

    for event_type in event_types:
        recorder.record(event_type, payload={"marker": event_type.value})

    trace = recorder.to_trace()

    assert len(trace.events) == len(event_types)
    assert [event.event_type for event in trace.events] == event_types


def test_recorder_enforces_monotonic_timestamps_and_step_indexes() -> None:
    base = datetime(2026, 3, 29, 12, 0, tzinfo=timezone.utc)
    recorder = TraceRecorder("run-002", started_at=base)

    first = recorder.record(
        EventType.SYSTEM_PROMPT,
        payload={"text": "hello"},
        timestamp=base + timedelta(seconds=1),
    )
    second = recorder.record(
        EventType.USER_TASK,
        payload={"task": "summarize"},
        timestamp=base + timedelta(seconds=2),
    )

    assert first.step_index == 0
    assert second.step_index == 1
    assert first.timestamp <= second.timestamp



def test_recorder_rejects_backward_timestamp() -> None:
    base = datetime(2026, 3, 29, 12, 0, tzinfo=timezone.utc)
    recorder = TraceRecorder("run-003", started_at=base)
    recorder.record(EventType.SYSTEM_PROMPT, timestamp=base + timedelta(seconds=5))

    with pytest.raises(ValueError):
        recorder.record(EventType.USER_TASK, timestamp=base + timedelta(seconds=4))



def test_trace_payload_integrity_and_json_serialization() -> None:
    recorder = TraceRecorder("run-004")
    payload = {
        "tool": "read_email",
        "arguments": {"email_id": "abc123"},
        "meta": {"trusted": False, "risk": "low"},
    }
    recorder.record(EventType.TOOL_CALL_REQUESTED, payload=payload)

    dumped = recorder.to_dict()
    event = dumped["events"][0]

    assert event["payload"]["tool"] == "read_email"
    assert event["payload"]["arguments"]["email_id"] == "abc123"
    assert event["payload"]["meta"]["trusted"] is False
