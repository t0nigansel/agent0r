from __future__ import annotations

import pytest

from act0r.adapters import (
    AdapterMessage,
    AdapterRequest,
    AdapterRuntimeError,
    OpenAICompatibleAdapter,
)


def _base_request() -> AdapterRequest:
    return AdapterRequest(messages=[AdapterMessage(role="user", content="hi")], step_index=0)


def test_openai_compatible_normalizes_openai_tool_call_shape() -> None:
    adapter = OpenAICompatibleAdapter(
        client=lambda payload: {
            "choices": [
                {
                    "finish_reason": "tool_calls",
                    "message": {
                        "content": "I will call a tool",
                        "tool_calls": [
                            {
                                "type": "function",
                                "function": {
                                    "name": "read_email",
                                    "arguments": '{"email_id":"abc"}',
                                },
                            }
                        ],
                    },
                }
            ]
        }
    )

    response = adapter.generate(_base_request())

    assert response.assistant_text == "I will call a tool"
    assert response.tool_calls[0].name == "read_email"
    assert response.tool_calls[0].arguments["email_id"] == "abc"
    assert response.is_final is False


def test_openai_compatible_normalized_shape_passthrough() -> None:
    adapter = OpenAICompatibleAdapter(
        client=lambda payload: {
            "assistant_text": "done",
            "tool_calls": [],
            "is_final": True,
        }
    )

    response = adapter.generate(_base_request())

    assert response.assistant_text == "done"
    assert response.is_final is True


def test_openai_compatible_rejects_invalid_tool_arguments_json() -> None:
    adapter = OpenAICompatibleAdapter(
        client=lambda payload: {
            "choices": [
                {
                    "finish_reason": "tool_calls",
                    "message": {
                        "content": "bad args",
                        "tool_calls": [
                            {
                                "type": "function",
                                "function": {
                                    "name": "read_email",
                                    "arguments": "{bad-json}",
                                },
                            }
                        ],
                    },
                }
            ]
        }
    )

    with pytest.raises(AdapterRuntimeError):
        adapter.generate(_base_request())
