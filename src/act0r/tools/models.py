from __future__ import annotations

from enum import Enum
from pathlib import Path
from typing import Any, Dict, Optional

from pydantic import BaseModel, ConfigDict, Field


class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class TrustLevel(str, Enum):
    UNTRUSTED = "untrusted"
    TRUSTED = "trusted"


class ToolSpec(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1)
    risk_level: RiskLevel = RiskLevel.LOW
    trust_level: TrustLevel = TrustLevel.UNTRUSTED
    has_side_effects: bool = False
    requires_confirmation: bool = False
    description: Optional[str] = None


class ToolExecutionContext(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    scenario_id: Optional[str] = None
    fixtures: Dict[str, Any] = Field(default_factory=dict)
    ephemeral_memory: Dict[str, Any] = Field(default_factory=dict)
    safe_fixture_root: Optional[Path] = None


class ToolResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    tool_name: str
    risk_level: RiskLevel
    trust_level: TrustLevel
    has_side_effects: bool
    requires_confirmation: bool
    blocked: bool = False
    output: Any
    message: Optional[str] = None
