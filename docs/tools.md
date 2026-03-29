# Tool Layer (MVP)

`act0r` uses a deterministic, sandboxed tool layer for agent-security testing.

## Components

- `ToolSpec`: static metadata for each tool (risk, trust, side effects, confirmation).
- `ToolResult`: structured output carrying the metadata with each execution result.
- `ToolRegistry`: deterministic registry for registration and lookup.
- Fake tools: safe local implementations that never perform uncontrolled side effects.

## Safety defaults

- All tool outputs are marked `untrusted` by default.
- High-risk tools (`write_memory`, `export_data`, `send_email`) return blocked/sandboxed results.
- File listing is limited to a configured safe fixture root.

## Included fake tools

- `read_email`
- `search_docs`
- `fetch_page`
- `write_memory`
- `export_data`
- `send_email`
- `list_files`
- `read_doc`
