# Runner (MVP)

The `AgentRunner` orchestrates one scenario run against a target adapter.

## Runtime flow

1. load scenario, fixtures, and tool set
2. send system prompt + user task to adapter
3. execute a bounded step loop
4. intercept and execute tool calls through registry
5. record all events through `TraceRecorder`
6. stop on completion or safe stop conditions

## Safe stop conditions

- adapter signals completion
- max step count reached
- blocked high-risk action
- unrecoverable adapter error

## Output

A `RunResult` includes:
- `status`
- `steps_executed`
- `final_response`
- complete structured `trace`
