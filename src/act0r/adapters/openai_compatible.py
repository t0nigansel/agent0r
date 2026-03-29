from __future__ import annotations

import json
from typing import Any, Callable, Dict, List, Optional

from .base import AgentAdapter
from .errors import AdapterRuntimeError
from .models import AdapterRequest, AdapterResponse, AdapterToolCall


class OpenAICompatibleAdapter(AgentAdapter):
    def __init__(
        self,
        *,
        model: str = "openai-compatible-model",
        client: Optional[Callable[[Dict[str, Any]], Dict[str, Any]]] = None,
    ) -> None:
        self.model = model
        self.client = client

    def generate(self, request: AdapterRequest) -> AdapterResponse:
        if self.client is None:
            raise AdapterRuntimeError("OpenAI-compatible adapter requires a client callable.")

        payload = {
            "model": self.model,
            "messages": [message.model_dump() for message in request.messages],
            "tools": [
                {
                    "type": "function",
                    "function": {
                        "name": tool.name,
                        "description": tool.description or "",
                        "parameters": {"type": "object"},
                    },
                }
                for tool in request.available_tools
            ],
        }

        try:
            raw = self.client(payload)
        except Exception as exc:
            raise AdapterRuntimeError("OpenAI-compatible client call failed: {}".format(exc)) from exc

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

        choices = raw.get("choices")
        if not choices:
            raise AdapterRuntimeError("OpenAI-compatible response missing choices.")

        first = choices[0]
        message = first.get("message", {})
        assistant_text = message.get("content") or ""

        tool_calls = _parse_openai_tool_calls(message.get("tool_calls", []))
        finish_reason = first.get("finish_reason") or raw.get("finish_reason")
        is_final = bool(finish_reason and finish_reason not in {"tool_calls", "function_call"}) and not tool_calls

        return AdapterResponse(
            assistant_text=assistant_text,
            tool_calls=tool_calls,
            is_final=is_final,
            raw_response=raw,
        )


def _parse_openai_tool_calls(raw_tool_calls: List[Dict[str, Any]]) -> List[AdapterToolCall]:
    parsed: List[AdapterToolCall] = []
    for item in raw_tool_calls:
        function = item.get("function", {})
        name = function.get("name")
        if not name:
            raise AdapterRuntimeError("OpenAI-compatible tool call missing function name.")

        raw_args = function.get("arguments", {})
        if isinstance(raw_args, str):
            try:
                arguments = json.loads(raw_args) if raw_args.strip() else {}
            except json.JSONDecodeError as exc:
                raise AdapterRuntimeError(
                    "OpenAI-compatible tool call arguments were not valid JSON."
                ) from exc
        elif isinstance(raw_args, dict):
            arguments = raw_args
        else:
            raise AdapterRuntimeError(
                "OpenAI-compatible tool call arguments must be a JSON string or object."
            )

        parsed.append(AdapterToolCall(name=name, arguments=arguments))

    return parsed
