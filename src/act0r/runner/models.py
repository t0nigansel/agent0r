from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from act0r.evaluation import RunEvaluation
from act0r.trace.models import RunTrace


class RunStatus(str, Enum):
    COMPLETED = "completed"
    STOPPED_MAX_STEPS = "stopped_max_steps"
    STOPPED_BLOCKED_CRITICAL_ACTION = "stopped_blocked_critical_action"
    STOPPED_ADAPTER_ERROR = "stopped_adapter_error"


class RunResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    run_id: str = Field(min_length=1)
    scenario_id: str = Field(min_length=1)
    status: RunStatus
    steps_executed: int = Field(ge=0)
    trace: RunTrace
    evaluation: Optional[RunEvaluation] = None
    stop_reason: Optional[str] = None
    final_response: Optional[str] = None
