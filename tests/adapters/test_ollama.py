from __future__ import annotations

import pytest

from act0r.adapters import AdapterMessage, AdapterRequest, AdapterRuntimeError, OllamaAdapter


def _base_request() -> AdapterRequest:
    return AdapterRequest(messages=[AdapterMessage(role="user", content="hi")], step_index=0)


def test_ollama_normalizes_tool_call_shape() -> None:
    adapter = OllamaAdapter(
        client=lambda payload: {
            "done": False,
            "message": {
                "content": "calling tool",
                "tool_calls": [
                    {
                        "function": {
                            "name": "search_docs",
                            "arguments": {"query": "launch checklist"},
                        }
                    }
                ],
            },
        }
    )

    response = adapter.generate(_base_request())

    assert response.assistant_text == "calling tool"
    assert response.tool_calls[0].name == "search_docs"
    assert response.tool_calls[0].arguments["query"] == "launch checklist"
    assert response.is_final is False


def test_ollama_normalized_shape_passthrough() -> None:
    adapter = OllamaAdapter(
        client=lambda payload: {
            "assistant_text": "done",
            "is_final": True,
            "tool_calls": [],
        }
    )

    response = adapter.generate(_base_request())

    assert response.assistant_text == "done"
    assert response.is_final is True


def test_ollama_rejects_non_object_tool_arguments() -> None:
    adapter = OllamaAdapter(
        client=lambda payload: {
            "done": False,
            "message": {
                "content": "calling tool",
                "tool_calls": [
                    {
                        "function": {
                            "name": "search_docs",
                            "arguments": "bad-args",
                        }
                    }
                ],
            },
        }
    )

    with pytest.raises(AdapterRuntimeError):
        adapter.generate(_base_request())
