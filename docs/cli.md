# CLI (MVP)

`act0r` includes an operator CLI:

- `act0r list-scenarios`
- `act0r run`
- `act0r run-all`
- `act0r report`
- `act0r ui`

## Notes

- default execution uses deterministic local mock adapter behavior
- runs are persisted to SQLite
- one Markdown report is written per run
- commands return non-zero exit code on failure
