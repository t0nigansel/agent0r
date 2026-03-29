"""Target backend adapters for agent runner."""

from .base import AgentAdapter
from .errors import AdapterRuntimeError
from .models import AdapterMessage, AdapterRequest, AdapterResponse, AdapterToolCall
from .ollama import OllamaAdapter
from .openai_compatible import OpenAICompatibleAdapter

__all__ = [
    "AdapterMessage",
    "AdapterRequest",
    "AdapterResponse",
    "AdapterRuntimeError",
    "AdapterToolCall",
    "AgentAdapter",
    "OllamaAdapter",
    "OpenAICompatibleAdapter",
]
