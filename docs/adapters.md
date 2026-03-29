# Adapters (MVP)

Adapters normalize backend-specific model responses into a shared shape.

## Shared contract

- input: `AdapterRequest`
- output: `AdapterResponse`
- normalized tool calls: `AdapterToolCall`

## Included adapters

- `OpenAICompatibleAdapter`
- `OllamaAdapter`

Both adapters support:
- normalized direct response shape (`assistant_text`, `tool_calls`, `is_final`)
- provider-style response parsing
- deterministic tool-call argument normalization
