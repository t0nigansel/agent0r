from __future__ import annotations

from typing import Any, Callable, Dict, List, Optional

from .base import AgentAdapter
from .errors import AdapterRuntimeError
from .models import AdapterRequest, AdapterResponse, AdapterToolCall


class OllamaAdapter(AgentAdapter):
    def __init__(
        self,
        *,
        model: str = "ollama-model",
        client: Optional[Callable[[Dict[str, Any]], Dict[str, Any]]] = None,
    ) -> None:
        self.model = model
        self.client = client

    def generate(self, request: AdapterRequest) -> AdapterResponse:
        if self.client is None:
            raise AdapterRuntimeError("Ollama adapter requires a client callable.")

        payload = {
            "model": self.model,
            "messages": [message.model_dump() for message in request.messages],
            "tools": [
                {
                    "type": "function",
                    "function": {
                        "name": tool.name,
                        "description": tool.description or "",
                    },
                }
                for tool in request.available_tools
            ],
        }

        try:
            raw = self.client(payload)
        except Exception as exc:
            raise AdapterRuntimeError("Ollama client call failed: {}".format(exc)) from exc

        return self._normalize(raw)

    def _normalize(self, raw: Dict[str, Any]) -> AdapterResponse:
        if "assistant_text" in raw or "tool_calls" in raw:
            tool_calls = [
                AdapterToolCall.model_validate(tool_call)
                for tool_call in raw.get("tool_calls", [])
            ]
            return AdapterResponse(
                assistant_text=raw.get("assistant_text", "") or "",
                tool_calls=tool_calls,
                is_final=bool(raw.get("is_final", False)),
                raw_response=raw,
            )

        message = raw.get("message", {})
        assistant_text = message.get("content") or ""

        tool_calls = _parse_ollama_tool_calls(message.get("tool_calls", []))
        is_final = bool(raw.get("done", False)) and not tool_calls

        return AdapterResponse(
            assistant_text=assistant_text,
            tool_calls=tool_calls,
            is_final=is_final,
            raw_response=raw,
        )


def _parse_ollama_tool_calls(raw_tool_calls: List[Dict[str, Any]]) -> List[AdapterToolCall]:
    parsed: List[AdapterToolCall] = []

    for item in raw_tool_calls:
        function = item.get("function", {})
        name = function.get("name")
        arguments = function.get("arguments", {})

        if not name:
            raise AdapterRuntimeError("Ollama tool call missing function name.")
        if not isinstance(arguments, dict):
            raise AdapterRuntimeError("Ollama tool call arguments must be an object.")

        parsed.append(AdapterToolCall(name=name, arguments=arguments))

    return parsed
