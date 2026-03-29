# PROJECT.md

## Project Name

**act0r**

A local-first security testing tool for LLM agents.

It is the sibling project to **prompt0r**.


---

## Vision

Modern AI systems are increasingly built as **agents**.

The real risk is often not only what an AI says.
The real risk is what an agent **does**:

- which tools it calls
- which documents it trusts
- whether it can be redirected
- whether it stores poisoned memory
- whether it exports data
- whether it performs side effects without permission

`act0r` exists to test exactly that.

It should help developers and security engineers understand whether an agent:

- stays aligned with user intent
- resists indirect prompt injection
- uses tools safely
- respects policy boundaries
- avoids unsafe persistence
- avoids over-autonomous behavior

The project should feel like a practical operator tool, not a research toy.


---

## Relationship to prompt0r

`prompt0r` and `act0r` belong together.

### `prompt0r`
Tests prompts against models.

Main question:
> What does the model say when attacked?

### `act0r`
Tests agent workflows, tool use, and actions.

Main question:
> What does the agent do when attacked?

They should feel like sibling products:

- similar naming
- similar visual language
- similar operator workflow
- similar dark technical UI
- similar project philosophy


---

## Product Goal

Build a practical MVP that allows a user to:

1. define security scenarios for an agent
2. run an agent against those scenarios
3. expose controlled fake or wrapped tools
4. capture the full execution trace
5. detect policy violations deterministically
6. generate a readable Markdown report
7. inspect runs in a UI similar to `prompt0r`

The product should be useful early, even before advanced features exist.


---

## Product Philosophy

This tool should be:

- **local-first**
- **testable**
- **deterministic where possible**
- **safe by default**
- **clear rather than clever**
- **useful for iterative engineering**
- **easy for agents to extend**

It should not feel academic.
It should feel like a real engineering tool.

The primary audience is:

- builders of LLM agents
- security engineers
- red teamers
- developers working on tool-using systems
- researchers who want practical workflow testing


---

## MVP Scope

The MVP should support these core capabilities:

### 1. Scenario-driven testing
Users define a scenario in a structured file.

A scenario includes:

- task
- system prompt
- tools
- fixtures
- policy expectations
- security focus

### 2. Agent execution
A target agent is run inside a controlled environment.

### 3. Tool sandboxing
Tools are fake or safely wrapped.
No uncontrolled side effects.

### 4. Policy enforcement
Unsafe behavior is detected via explicit rules.

### 5. Trace capture
Important events are recorded in structured form.

### 6. Deterministic evaluation
The MVP should not rely on vague LLM judging for correctness.

### 7. Markdown reporting
Each run should generate a readable Markdown report.

### 8. Operator UI
A dark, minimal interface similar to `prompt0r` should allow users to inspect runs.


---

## What the MVP Must Not Become

The MVP must stay focused.

Not in scope unless later requested:

- real email sending
- real browser automation
- real destructive shell execution
- cloud-first architecture
- multi-user SaaS
- auth and account systems
- enterprise policy management
- live attack infrastructure
- highly dynamic autonomous red teaming
- heavy orchestration frameworks without need
- fancy dashboards before core engine works

The core engine comes first.


---

## Primary Use Cases

### Use Case 1: Indirect Prompt Injection
A retrieved email, web page, or document contains a malicious instruction.

The tool should detect whether the agent:

- follows the malicious text
- ignores the malicious text
- treats it as untrusted data
- performs unsafe actions because of it

### Use Case 2: Tool Abuse
The agent uses tools it does not need or should not use.

The tool should detect:

- unnecessary tool calls
- privileged tool calls
- unsafe tool parameters
- blocked vs attempted actions

### Use Case 3: Memory Poisoning
A document tries to persuade the agent to write unsafe long-term instructions into memory.

The tool should detect:

- attempted memory writes
- successful poisoned writes
- later trust in poisoned memory

### Use Case 4: Goal Hijacking
The agent drifts away from the user’s goal due to embedded instructions.

The tool should detect:

- divergence from intended task
- agent obedience to untrusted content
- unsafe autonomy

### Use Case 5: Unauthorized Export or Side Effects
The agent attempts to export data, send a message, or take an outbound action without permission.

The tool should detect:

- attempted exfiltration
- unauthorized side-effect actions
- policy boundary violations


---

## Product Shape

`act0r` should be a **modular monolith**.

That means:

- one codebase
- clear internal modules
- simple deployment
- low ceremony
- easy local execution
- clean separation of concerns

Suggested internal domains:

- scenarios
- runners
- tools
- policies
- traces
- evaluation
- reporting
- persistence
- adapters
- ui


---

## UX and UI Direction

The interface should look and feel similar to `prompt0r`.

### UI goals
- dark theme
- left sidebar
- compact navigation
- dense but readable tables
- small practical buttons
- operator-style workflow
- minimal distractions
- technical appearance
- clear inspection views
- consistency over novelty

### It should not be
- playful
- glossy
- marketing-heavy
- full of visual decoration
- over-animated
- cluttered

### Core navigation areas
- Targets
- Scenarios
- Runs
- Reports / Analysis

### Typical user flow
1. choose target
2. choose scenario
3. run test
4. inspect run
5. inspect violations
6. inspect report
7. compare and improve agent

The product should feel like a working console for agent safety testing.


---

## Core Concepts

### Scenario
A structured security test definition.

### Target
The model or agent system being tested.

### Tool
A callable capability available to the target agent.

### Policy
A set of explicit rules defining allowed and disallowed behavior.

### Trace
The structured record of what happened during execution.

### Violation
A detected breach of policy or safe behavior.

### Verdict
The final assessment of the run.


---

## Technical Direction

### Language
Python 3.12

### Storage
SQLite for MVP

### Schemas
Pydantic

### Config / Scenarios
YAML

### Reports
Markdown

### UI
Keep aligned with existing `prompt0r` approach and design language

### Adapters
Start small:
- Ollama
- OpenAI-compatible adapter

### Safety
All risky tools must be fake, sandboxed, or wrapped safely.


---

## Design Principles

### 1. Safety first
This project tests dangerous behavior.
It must not create dangerous behavior.

### 2. Deterministic first
Core grading should be rule-based wherever possible.

### 3. Inspectability first
A human should be able to understand why a run failed.

### 4. Local-first
The tool should work on a developer machine without complex setup.

### 5. Small-step architecture
Prefer a working simple version over a grand unfinished system.

### 6. Strong defaults
Untrusted content should be treated as untrusted by default.

### 7. Side effects are suspicious
Any outbound or persistent action should be visible and policy-checked.


---

## Security Model

The security model of `act0r` should assume:

- documents may contain malicious instructions
- tool outputs may contain malicious instructions
- retrieved content is not inherently trustworthy
- models may over-follow the latest instruction
- agents may confuse data with instruction
- persistent memory is dangerous if poorly controlled
- high-risk tools must be tightly controlled

### Default trust rule
**All external or retrieved content is untrusted unless explicitly marked otherwise.**

This includes:

- search results
- email bodies
- documents
- webpage content
- tool output text
- metadata
- OCR text
- comments in markup
- structured fields in JSON/YAML/XML/CSV

This default is central to the product.


---

## Reporting Philosophy

The first output format is Markdown.

Reports must be:

- readable
- concise
- structured
- practical
- useful for engineers

A good report should answer:

- what was the scenario?
- what should the agent have done?
- what actually happened?
- which tools were called?
- what violated policy?
- how severe was it?
- what should be fixed?

Reports should not feel like raw logs.
They should feel like a security assessment summary.


---

## Example Findings This Tool Should Surface

- Agent followed malicious instruction embedded in email
- Agent attempted unauthorized export tool call
- Agent wrote attacker-controlled text into memory
- Agent treated tool output as trusted instruction
- Agent drifted away from the user’s task
- Agent attempted persistent behavior change
- Agent called high-risk tool without explicit approval

These are the kinds of results the tool should make obvious.


---

## Initial Success Criteria

The project is successful in its MVP form when:

- a scenario can be defined in YAML
- a target can be run against that scenario
- fake tools can be exposed safely
- events are captured in structured form
- policy violations are detected
- a verdict is produced
- a Markdown report is written
- the run can be viewed in a UI similar to `prompt0r`

The MVP does not need to be perfect.
It needs to be useful, clear, and extensible.


---

## Suggested Initial Scenario Pack

The first version should include at least these scenarios:

1. benign email summary
2. email with embedded malicious instruction
3. search result tool hijack
4. memory poisoning attempt
5. unauthorized export attempt
6. goal hijack through retrieved document

These scenarios are enough to validate the engine.


---

## Long-Term Direction

After MVP, the project may grow into:

- broader scenario packs
- multi-agent handoff testing
- visual / OCR injection testing
- differential testing across models
- richer reporting
- PDF export
- run comparison views
- replay / trace visualizer
- policy packs
- more adapters
- browser agent testing

But these must not delay the MVP.


---

## Build Priorities

Build in this order unless a strong reason appears otherwise:

### Priority 1
Core engine:
- schema
- loader
- tools
- runner
- trace recorder

### Priority 2
Policy and evaluation:
- rule checks
- violation model
- verdict logic

### Priority 3
Reporting:
- Markdown output
- readable summaries

### Priority 4
Persistence:
- SQLite
- repositories

### Priority 5
UI:
- run history
- run details
- report view
- scenario/target views

### Priority 6
Polish:
- tests
- consistency
- UX refinement
- expanded scenario coverage


---

## Constraints for Coding Agents

Coding agents working on this project should:

- work with high autonomy
- avoid asking for confirmation on small decisions
- choose the simpler safer path by default
- keep changes incremental
- keep docs updated
- avoid over-engineering
- avoid speculative features
- prefer vertical slices
- respect the MVP boundary
- mirror `prompt0r` where appropriate

Coding agents should treat this file and related project docs as the source of truth.


---

## Source of Truth Files

The project should maintain and rely on these files:

- `PROJECT.md`
- `ACT0R_SPEC.md`
- `AGENT.md`
- `TASKS.md`
- `UI_GUIDE.md`

If one of these files is missing, it should be created rather than silently ignored.


---

## Final Project Statement

`act0r` should become a practical, local-first, operator-style tool for testing whether LLM agents behave safely under pressure.

It should help answer one core question:

> Can this agent be trusted to act safely when its environment is adversarial?

That answer should be visible through:

- scenarios
- traces
- policy checks
- violations
- verdicts
- reports
- a clear UI