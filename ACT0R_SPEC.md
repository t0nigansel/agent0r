# ACT0R_SPEC.md

## Purpose

This file defines the implementation-facing MVP specification for `act0r`.

It complements:
- `PROJECT.md` (vision and scope)
- `AGENT.md` (autonomous implementation behavior)
- `TASKS.md` (execution backlog)
- `UI_GUIDE.md` (visual and UX direction)

When details are missing, prefer:
1. safe defaults
2. deterministic behavior
3. inspectable outputs
4. narrow MVP scope

## MVP boundaries

The MVP is local-first and must avoid uncontrolled side effects.

Allowed in MVP:
- deterministic scenario files
- fake or sandboxed tool behavior
- structured event capture
- deterministic policy/evaluation checks
- markdown reporting
- operator-first UI

Not allowed in MVP:
- real outbound email sending
- uncontrolled browser automation
- arbitrary host shell execution
- cloud-first architecture
- account/auth systems

## Runtime model

A run executes a scenario against a target adapter under guardrails.

High-level flow:
1. load scenario YAML
2. validate schema
3. resolve fixture references
4. run target in bounded loop
5. intercept tool calls
6. apply policy checks
7. produce deterministic verdict
8. write markdown report

## Scenario format (MVP v0)

Scenario files are YAML mappings with explicit fields.

Required fields:
- `id` (`SCN-###`)
- `title`
- `system_prompt`
- `user_task`

Optional fields:
- `description`
- `category`
- `security_focus` (list of strings)
- `tags` (list of strings)
- `tools` (list of tool constraints)
- `fixtures` (mapping of fixture keys to reference)
- `policy_expectations` (list of expected policy outcomes)

Fixture reference forms:
- shorthand string path
- object with `path`, `format`, `trusted`, `required`, `description`

Fixture path behavior:
- relative paths resolve from the scenario file directory
- absolute paths are allowed for local workflows
- missing required fixtures fail closed

Supported fixture formats:
- `text`
- `json`
- `yaml`

## Validation behavior

Validation must be explicit and readable.

Failure classes:
- YAML parse errors
- schema validation errors
- missing fixture errors
- fixture decode errors

Error messages should:
- include scenario path
- include field location when available
- include enough context to fix quickly

## Determinism expectations

For loading and schema behavior:
- same input file must produce the same structured output
- scenario directory loads should be filename-sorted
- validation failure output should be stable and inspectable

## Directory expectations (current MVP base)

- `src/act0r/` core Python package
- `src/act0r/scenarios/` scenario schema/loading modules
- `tests/` unit and integration tests
- `docs/scenarios/` scenario format documentation

## Security posture for this phase

This phase does not execute real tools.
It only loads scenario definitions and local fixture content.

Principles:
- fail closed on malformed or missing required data
- treat fixture-derived content as untrusted by default
- keep behavior inspectable and test-covered
