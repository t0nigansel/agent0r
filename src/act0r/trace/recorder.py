from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from .models import EventType, RunTrace, TraceEvent


class TraceRecorder:
    def __init__(self, run_id: str, *, started_at: Optional[datetime] = None) -> None:
        start_time = started_at or datetime.now(timezone.utc)
        self._trace = RunTrace(run_id=run_id, started_at=start_time)

    @property
    def run_id(self) -> str:
        return self._trace.run_id

    @property
    def events(self) -> List[TraceEvent]:
        return list(self._trace.events)

    def record(
        self,
        event_type: EventType,
        payload: Optional[Dict[str, Any]] = None,
        *,
        timestamp: Optional[datetime] = None,
    ) -> TraceEvent:
        event_time = timestamp or datetime.now(timezone.utc)

        if self._trace.events:
            previous = self._trace.events[-1]
            if event_time < previous.timestamp:
                raise ValueError(
                    "Event timestamp cannot be earlier than the previous event timestamp."
                )

        event = TraceEvent(
            step_index=len(self._trace.events),
            timestamp=event_time,
            event_type=event_type,
            payload=payload or {},
        )
        self._trace.events.append(event)
        return event

    def to_trace(self) -> RunTrace:
        return RunTrace.model_validate(self._trace.model_dump())

    def to_dict(self) -> Dict[str, Any]:
        return self._trace.model_dump(mode="json")
