from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Set

from pydantic import BaseModel, ConfigDict, Field


class AgentRole(str, Enum):
    PARENT = "parent"
    SUB_AGENT = "sub_agent"


class WorkflowSeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class AgentNode(BaseModel):
    model_config = ConfigDict(extra="forbid")

    agent_id: str = Field(min_length=1)
    role: AgentRole
    privileges: Set[str] = Field(default_factory=set)
    policy_context: Dict[str, Any] = Field(default_factory=dict)


class HandoffRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")

    from_agent_id: str = Field(min_length=1)
    to_agent_id: str = Field(min_length=1)
    task: str = Field(min_length=1)
    requested_privileges: List[str] = Field(default_factory=list)
    granted_privileges: List[str] = Field(default_factory=list)
    propagated_policy: Dict[str, Any] = Field(default_factory=dict)


class MultiAgentSession(BaseModel):
    model_config = ConfigDict(extra="forbid")

    session_id: str = Field(min_length=1)
    agents: Dict[str, AgentNode]
    handoffs: List[HandoffRecord] = Field(default_factory=list)


class WorkflowFinding(BaseModel):
    model_config = ConfigDict(extra="forbid")

    check_id: str = Field(min_length=1)
    severity: WorkflowSeverity
    message: str = Field(min_length=1)
    handoff_index: int = Field(ge=0)


class WorkflowAnalysis(BaseModel):
    model_config = ConfigDict(extra="forbid")

    session_id: str = Field(min_length=1)
    findings: List[WorkflowFinding] = Field(default_factory=list)

    @property
    def passed(self) -> bool:
        return len(self.findings) == 0
