from __future__ import annotations

from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field

from act0r.tools.models import ToolSpec


class AdapterMessage(BaseModel):
    model_config = ConfigDict(extra="forbid")

    role: Literal["system", "user", "assistant", "tool"]
    content: str = ""


class AdapterToolCall(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1)
    arguments: Dict[str, Any] = Field(default_factory=dict)


class AdapterRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    messages: List[AdapterMessage] = Field(default_factory=list)
    available_tools: List[ToolSpec] = Field(default_factory=list)
    step_index: int = Field(ge=0, default=0)


class AdapterResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    assistant_text: str = ""
    tool_calls: List[AdapterToolCall] = Field(default_factory=list)
    is_final: bool = False
    raw_response: Optional[Dict[str, Any]] = None
