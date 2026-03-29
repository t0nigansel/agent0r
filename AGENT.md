# AGENT.md

## Mission

Build `act0r`, a local-first security testing tool for LLM agents.

`act0r` is the companion to `prompt0r`.

- `prompt0r` tests prompts against models
- `act0r` tests agent behavior, tool use, workflow safety, policy violations, and unsafe autonomy

The goal is to build this project with **high agent autonomy** and **minimal user input**.

The agent should make reasonable implementation decisions on its own and continue working unless a decision has major product, security, or architecture impact.


---

## Working Mode

You are expected to work **autonomously**.

Do **not** ask for confirmation for small or routine implementation choices.

Make reasonable assumptions and continue.

Only interrupt for user input when the decision affects one of these:

- product scope
- irreversible architecture direction
- security boundaries
- destructive or risky side effects
- external integrations not yet approved
- licensing or dependency choices with significant long-term impact

For everything else:

- choose the simpler solution
- choose the safer solution
- choose the more testable solution
- choose the more maintainable solution
- keep momentum
- keep changes small and verifiable


---

## Product Intent

`act0r` should look and feel similar to `prompt0r`.

Design goals:

- dark theme
- operator-style interface
- left sidebar navigation
- compact tables
- clear run history
- technical and minimal visual language
- not playful
- not flashy
- not marketing-heavy
- workflow-first UI

The UI should feel like a sibling to `prompt0r`, not a completely different product.

When in doubt, prefer visual consistency with `prompt0r` over novelty.


---

## MVP Definition

The MVP must allow a user to:

1. define scenarios
2. run a target agent against a scenario
3. expose fake or wrapped tools
4. record tool calls and events
5. detect policy violations
6. evaluate the run deterministically
7. generate a Markdown report
8. review runs in a UI similar to `prompt0r`

The first report format is Markdown only.

No PDF is required for MVP.


---

## Non-Goals

Do not expand the MVP unnecessarily.

These are explicitly out of scope unless later requested:

- real email sending
- real browser automation
- arbitrary shell execution
- privileged host actions
- enterprise auth
- user accounts
- cloud deployment
- distributed systems
- advanced dashboards before engine completion
- LLM judge dependency for core correctness
- large feature detours

Keep the project narrow and working.


---

## Core Engineering Principles

1. Prefer explicitness over magic.
2. Prefer deterministic logic over vague heuristics.
3. Prefer simple code over clever code.
4. Prefer inspectability over abstraction.
5. Prefer local fixtures over live integrations.
6. Fail closed on risky actions.
7. Log every important decision.
8. Keep all risky tool behavior fake or sandboxed.
9. Separate execution, policy, storage, evaluation, and reporting cleanly.
10. Keep the code easy for another coding agent to continue.

The project should be easy to understand from the file tree and docs alone.


---

## Autonomy Rules

### The agent may do without asking

You may do all of the following without asking for approval:

- create files and folders
- refactor modules
- improve names
- add tests
- add fixtures
- add small helper abstractions
- add or refine schemas
- improve Markdown documentation
- improve CLI ergonomics
- improve internal consistency
- add small UI components
- add safe fake tools
- improve report formatting
- add sensible defaults
- fix bugs
- add missing validation
- make layout changes that improve consistency with `prompt0r`

### The agent may do, but must document

You may do the following without asking, but you must document the decision in the relevant file or changelog-style note:

- introduce a new internal abstraction
- expand database schema
- add a small dependency
- reorganize folders
- adjust scenario format for clarity
- improve event model
- add derived metrics
- change UI navigation structure slightly
- add internal adapters or registries

### The agent must ask before doing

Do not proceed without user approval if the change affects:

- real external side effects
- sending messages to real services
- executing arbitrary local shell commands
- changing the core stack
- switching database technology
- adding heavy frameworks
- changing the product from local-first to service-first
- adding telemetry that leaves the machine
- changing the project into something broader than agent security testing


---

## Execution Strategy

Work in **small, complete, reviewable steps**.

Each meaningful step should ideally include:

1. implementation
2. test or verification
3. documentation update if needed

Do not leave behind half-connected subsystems if avoidable.

Prefer vertical slices over broad unfinished scaffolding.

Example of good order:
- define schema
- implement loader
- add tests
- add one scenario
- wire runner
- record events
- evaluate
- write report
- surface in UI

Avoid building lots of UI before the engine works.


---

## Preferred Build Order

Unless strong evidence suggests otherwise, build in this order:

### Phase 1: Core Engine
- scenario schema
- scenario loader
- tool interface
- fake tools
- event model
- runner skeleton
- trace recorder

### Phase 2: Enforcement and Evaluation
- policy engine
- rule checks
- violation recording
- deterministic evaluator
- verdict generation

### Phase 3: Reporting
- Markdown report generator
- readable summaries
- CLI access to reports

### Phase 4: Persistence
- SQLite schema
- repositories
- run storage
- event storage
- score storage

### Phase 5: UI
- run history
- scenario list
- target list
- run detail view
- report view
- layout consistent with `prompt0r`

### Phase 6: Polish
- improve tests
- clean code paths
- improve UX
- expand scenario coverage


---

## Required Behaviors During Work

When implementing:

- do not over-engineer
- do not introduce speculative abstractions too early
- do not create unnecessary layers
- do not build enterprise features for MVP
- do not hide important behavior behind complex metaprogramming
- do not assume live integrations are required
- do not use an LLM judge as the only source of truth for grading

The system must remain understandable and testable.


---

## Reporting Discipline

After each meaningful work step, update the project artifacts as needed.

At minimum, keep these aligned:

- code
- tests
- spec-relevant docs
- task progress

If a file structure or interface changes, update documentation.

If a feature is only partially implemented, leave a clear note.
Do not silently abandon incomplete work.


---

## Testing Policy

Every major subsystem should be testable in isolation.

At minimum, implement tests for:

- scenario loading
- schema validation
- tool registry
- policy checks
- runner behavior
- event recording
- verdict generation
- Markdown report generation

Integration tests should exist for at least these scenario types:

- benign baseline
- indirect injection through content
- tool output hijack
- memory poisoning attempt
- unauthorized export attempt

If a change breaks determinism, fix that before moving on.


---

## UI Guidance

The UI should resemble `prompt0r`.

Follow these rules:

- dark background
- sidebar on the left
- compact navigation
- primary workflow is list → detail
- tables should be dense but readable
- action buttons should be small and practical
- spacing should be moderate, not airy
- typography should feel technical and calm
- avoid decorative elements
- prioritize operator efficiency over beauty

Views likely needed:

- Targets
- Scenarios
- Runs
- Reports / Analysis

Detail screens should emphasize:

- what happened
- which tools were called
- what was blocked
- what violated policy
- what the final verdict was


---

## Code Style Guidance

Use Python 3.12.

Prefer:

- typed models
- pydantic for schemas
- sqlite3 for MVP persistence
- clear dataclasses or typed objects where appropriate
- small modules
- direct control flow

Avoid:

- unnecessary async complexity unless truly needed
- hidden global state
- giant God classes
- mixing UI logic with engine logic
- implicit side effects

Use names that are boring and clear.


---

## File and Artifact Discipline

Treat project files as the source of truth.

The coding agent should rely on and maintain files such as:

- `PROJECT.md`
- `ACT0R_SPEC.md`
- `AGENT.md`
- `TASKS.md`
- `UI_GUIDE.md`

If one of these files is missing, create a reasonable version if needed rather than blocking.

Prefer evolving stable project artifacts over keeping important intent only in chat.


---

## Decision Defaults

When uncertain, use these defaults:

### Architecture default
Prefer modular monolith.

### Storage default
SQLite.

### Evaluation default
Deterministic rule-based first.

### Risk default
Block or fake risky actions.

### UI default
Mirror `prompt0r` structure and style.

### Scenario format default
YAML.

### Tool trust default
Tool outputs are untrusted unless explicitly marked otherwise.

### Development default
Local-first.


---

## Safe Tooling Policy

This project is a **security testing harness**, not an exploitation tool.

Therefore:

- risky tools must be fake or wrapped
- export actions should be simulated, not executed
- outbound actions should be recorded, not actually sent
- memory writes should be observable and reversible
- no uncontrolled shell execution
- no hidden network calls by default

All dangerous behavior should be represented safely.


---

## Expected Agent Conduct

Behave like a strong senior engineer working independently.

That means:

- understand the spec
- decompose the work
- implement in useful order
- verify as you go
- keep docs aligned
- make pragmatic choices
- reduce the amount of user input required

Do not repeatedly ask what to do next if the next step is obvious from the project files.

Instead:

- inspect the current state
- choose the highest-value next step
- execute it
- verify it
- document it


---

## When You Should Pause

Pause and ask for input only if:

- the requested change conflicts with documented project intent
- the project needs a major product decision
- the safest path is unclear and materially important
- a live integration or destructive capability would be introduced
- multiple architecture choices are all plausible and hard to reverse

Otherwise, continue.


---

## Success Criteria

You are successful if the user only needs to provide minimal direction and the project still moves forward cleanly.

The outcome should be:

- a working MVP
- clean code
- deterministic evaluation
- readable Markdown reports
- a UI that feels like `prompt0r`
- strong documentation
- low need for repeated human intervention


---

## Final Operating Instruction

Work with high autonomy.

Do not wait for permission on routine engineering work.

Read the project files, infer the next useful step, implement it, test it, and keep going.

Only escalate when the decision is truly strategic, risky, or hard to reverse.