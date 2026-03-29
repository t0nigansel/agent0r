# Persistence (MVP)

`act0r` uses SQLite for local-first persistence.

## Schema entities

- `scenarios`
- `runs`
- `events`
- `violations`
- `scores`

Schema is defined in `src/act0r/storage/schema.sql` and initialized automatically.

## Repository layer

- `ScenarioRepository`
- `RunRepository`
- `EventRepository`
- `ViolationRepository`
- `ScoreRepository`

All SQL remains localized to the storage layer.

## Stored-data workflows

`SQLiteStorage` supports:
- persisting full run bundles
- reloading persisted runs
- reconstructing `RunResult`
- regenerating Markdown reports from persisted run data
