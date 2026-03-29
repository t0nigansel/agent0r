# act0r

`act0r` is a local-first security testing tool for LLM agents.

It is the sibling project to `prompt0r`:
- `prompt0r` asks what a model says under attack.
- `act0r` asks what an agent does under attack.

## Current milestone

This repository currently includes:
- MVP foundation docs and Python package structure
- deterministic scenario schema and YAML loader
- fixture reference resolution and loading
- unit tests for valid/invalid scenario flows

## Quickstart

1. Create and activate a Python 3.9+ environment.
2. Install the package in editable mode:

```bash
python3 -m pip install -e .
```

3. Run tests:

```bash
python3 -m pytest
```

## Development notes

- Source code lives in `src/act0r`.
- Tests live in `tests`.
- MVP scenarios live in `scenarios/mvp`.
- Local scenario fixtures live in `scenarios/fixtures`.
- Scenario schema/loading is implemented in `act0r.scenarios`.
- Tool abstraction and fake tools are implemented in `act0r.tools`.
- Trace events and recorder are implemented in `act0r.trace`.
- Target backend adapters are implemented in `act0r.adapters`.
- Run orchestration is implemented in `act0r.runner`.
- Deterministic policy checks are implemented in `act0r.policy`.
- Deterministic scoring/verdicts are implemented in `act0r.evaluation`.
- Markdown run reporting is implemented in `act0r.reporting`.
- SQLite persistence is implemented in `act0r.storage`.
- Operator CLI is implemented in `act0r.cli`.
- UI operational app + local API server are in `ui/` and `act0r.ui_backend`.
- Scenario format docs are in `docs/scenarios/schema.md`.
- Tool layer docs are in `docs/tools.md`.
- Trace docs are in `docs/trace.md`.
- Adapter docs are in `docs/adapters.md`.
- Runner docs are in `docs/runner.md`.
- Policy docs are in `docs/policy.md`.
- Evaluation docs are in `docs/evaluation.md`.
- Reporting docs are in `docs/reporting.md`.
- Storage docs are in `docs/storage.md`.
- CLI docs are in `docs/cli.md`.
- UI run instructions are in `ui/README.md`.

The MVP remains intentionally narrow: fake or sandboxed behaviors only, deterministic checks first, and a UI style aligned with `prompt0r`.
