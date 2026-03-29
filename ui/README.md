# act0r UI

Phase 11 UI uses a local HTTP server with JSON APIs and static frontend assets.

## Start

From repository root:

```bash
act0r ui --host 127.0.0.1 --port 8080
```

Then open:

- `http://127.0.0.1:8080/`

## Operational views

- Targets: list/select execution targets
- Scenarios: list attack scenarios and run selected scenario
- Runs: inspect history, status/verdict, trace, tool calls, violations
- Reports / Analysis: render Markdown report, compare two runs, and download export
