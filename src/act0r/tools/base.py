from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

from .models import ToolExecutionContext, ToolResult, ToolSpec


class Tool(ABC):
    spec: ToolSpec

    @abstractmethod
    def execute(
        self,
        arguments: Optional[Dict[str, Any]] = None,
        context: Optional[ToolExecutionContext] = None,
    ) -> ToolResult:
        raise NotImplementedError


class BaseTool(Tool):
    spec: ToolSpec

    def _result(
        self,
        output: Any,
        *,
        blocked: bool = False,
        message: Optional[str] = None,
    ) -> ToolResult:
        return ToolResult(
            tool_name=self.spec.name,
            risk_level=self.spec.risk_level,
            trust_level=self.spec.trust_level,
            has_side_effects=self.spec.has_side_effects,
            requires_confirmation=self.spec.requires_confirmation,
            blocked=blocked,
            output=output,
            message=message,
        )
