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
- Scenario schema/loading is implemented in `act0r.scenarios`.
- Scenario format docs are in `docs/scenarios/schema.md`.

The MVP remains intentionally narrow: fake or sandboxed behaviors only, deterministic checks first, and a UI style aligned with `prompt0r`.
