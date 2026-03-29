# Trace Model (MVP)

`act0r` records run activity as ordered structured events.

## Event shape

Each `TraceEvent` includes:
- `step_index`: zero-based index in run order
- `timestamp`: UTC timestamp
- `event_type`: one of the supported event types
- `payload`: structured event details

## Supported event types

- `system_prompt`
- `user_task`
- `assistant_response`
- `tool_call_requested`
- `tool_call_executed`
- `tool_result`
- `policy_decision`
- `violation_detected`
- `run_stopped`
- `run_completed`

## Recorder guarantees

- step indexes are sequential
- timestamps cannot move backward
- payload data is preserved in JSON-serializable output
