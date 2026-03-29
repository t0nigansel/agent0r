from __future__ import annotations

from abc import ABC, abstractmethod

from .models import AdapterRequest, AdapterResponse


class AgentAdapter(ABC):
    @abstractmethod
    def generate(self, request: AdapterRequest) -> AdapterResponse:
        raise NotImplementedError
