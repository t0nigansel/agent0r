from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List

from pydantic import BaseModel, ConfigDict, Field, field_validator


class EventType(str, Enum):
    SYSTEM_PROMPT = "system_prompt"
    USER_TASK = "user_task"
    ASSISTANT_RESPONSE = "assistant_response"
    TOOL_CALL_REQUESTED = "tool_call_requested"
    TOOL_CALL_EXECUTED = "tool_call_executed"
    TOOL_RESULT = "tool_result"
    POLICY_DECISION = "policy_decision"
    VIOLATION_DETECTED = "violation_detected"
    RUN_STOPPED = "run_stopped"
    RUN_COMPLETED = "run_completed"


class TraceEvent(BaseModel):
    model_config = ConfigDict(extra="forbid")

    step_index: int = Field(ge=0)
    timestamp: datetime
    event_type: EventType
    payload: Dict[str, Any] = Field(default_factory=dict)

    @field_validator("timestamp")
    @classmethod
    def normalize_timestamp(cls, value: datetime) -> datetime:
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc)


class RunTrace(BaseModel):
    model_config = ConfigDict(extra="forbid")

    run_id: str = Field(min_length=1)
    started_at: datetime
    events: List[TraceEvent] = Field(default_factory=list)

    @field_validator("started_at")
    @classmethod
    def normalize_started_at(cls, value: datetime) -> datetime:
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc)
