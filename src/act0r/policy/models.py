from __future__ import annotations

from enum import Enum
from typing import List

from pydantic import BaseModel, ConfigDict, Field


class PolicyRuleId(str, Enum):
    P001 = "P-001"
    P002 = "P-002"
    P003 = "P-003"
    P004 = "P-004"
    P005 = "P-005"
    P006 = "P-006"


class PolicyOutcome(str, Enum):
    ALLOW = "allow"
    WARN = "warn"
    DENY = "deny"
    BLOCK = "block"


class ViolationSeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ViolationAction(str, Enum):
    BLOCKED = "blocked"
    ATTEMPTED = "attempted"
    COMPLETED = "completed"


class PolicyDecision(BaseModel):
    model_config = ConfigDict(extra="forbid")

    rule_id: PolicyRuleId
    outcome: PolicyOutcome
    severity: ViolationSeverity
    message: str = Field(min_length=1)
    evidence_event_indexes: List[int] = Field(default_factory=list)


class Violation(BaseModel):
    model_config = ConfigDict(extra="forbid")

    rule_id: PolicyRuleId
    severity: ViolationSeverity
    action: ViolationAction
    message: str = Field(min_length=1)
    evidence_event_indexes: List[int] = Field(default_factory=list)


class PolicyEvaluation(BaseModel):
    model_config = ConfigDict(extra="forbid")

    decisions: List[PolicyDecision] = Field(default_factory=list)
    violations: List[Violation] = Field(default_factory=list)
