from __future__ import annotations

from pathlib import Path
from typing import Iterable, Optional


class ScenarioLoadError(ValueError):
    """Raised when a scenario cannot be parsed, validated, or loaded."""

    def __init__(
        self,
        scenario_path: Path,
        message: str,
        *,
        details: Optional[Iterable[str]] = None,
    ) -> None:
        self.scenario_path = scenario_path
        self.message = message
        self.details = [detail for detail in (details or []) if detail]
        super().__init__(str(self))

    def __str__(self) -> str:
        base = f"{self.message}: {self.scenario_path}"
        if not self.details:
            return base
        formatted_details = "\n".join(f"- {detail}" for detail in self.details)
        return f"{base}\n{formatted_details}"
