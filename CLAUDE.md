# ACT0R_SPEC.md

## Purpose

`act0r` is a security test harness for LLM agents.

It does **not** primarily test what an agent says.
It tests what an agent **does**.

The system runs target agents in a controlled sandbox with fake or wrapped tools and evaluates whether the agent:

- uses tools it should not use
- uses tools with unsafe parameters
- is manipulated by indirect prompt injection
- stores untrusted content in memory
- exfiltrates data
- escalates privileges
- drifts away from the user’s actual goal
- violates explicit policy constraints

`act0r` is the companion tool to `prompt0r`.

- `prompt0r` = tests prompts against LLMs
- `act0r` = tests agent actions, tool use, and workflow safety


---

## MVP Goal

Build a local-first MVP that can:

1. define a scenario
2. expose a set of controlled tools to a target agent
3. run the agent against the scenario
4. capture all actions and intermediate events
5. evaluate the run against explicit security policies
6. produce a Markdown report

The first output format is **Markdown only**.
No PDF generation is required for the MVP.


---

## Non-Goals

The MVP should **not** try to do all of this:

- no real browser automation
- no real email sending
- no real shell execution on host
- no real external side effects
- no real privileged system integrations
- no multi-user web platform
- no full enterprise policy engine
- no autonomous red teaming at internet scale

Keep it small.
Keep it deterministic.
Keep it testable.


---

## Core Idea

A target agent receives:

- a system prompt / instructions
- a user task
- optional context documents
- a set of tools
- an execution environment
- a policy

The target agent then runs.

`act0r` records:

- model messages
- tool calls
- tool parameters
- tool outputs
- decision sequence
- policy violations
- suspicious behaviors
- final outcome

Then `act0r` grades the run.


---

## Key Security Risks To Test

The MVP should support scenarios covering these risks:

1. **Indirect Prompt Injection**
   - malicious text inside tool output
   - malicious text in documents
   - malicious text in web-like content
   - malicious text in email / search results / retrieved notes

2. **Tool Abuse**
   - calling tools not needed for the task
   - calling high-privilege tools without justification
   - using tools with unsafe parameters

3. **Goal Hijacking**
   - agent abandons user goal
   - agent follows malicious instructions from untrusted content

4. **Memory Poisoning**
   - agent stores malicious or untrusted instructions in memory
   - agent later uses poisoned memory as trusted truth

5. **Data Exfiltration**
   - agent attempts to retrieve and output sensitive data
   - agent attempts to export data through tools

6. **Privilege Escalation**
   - agent moves from low-risk actions to high-risk actions
   - agent uses tools outside the allowed scope

7. **Unsafe Persistence**
   - agent sets future triggers or persistent rules
   - agent modifies long-term state without permission

8. **Over-Autonomy**
   - agent performs side-effect actions without explicit user approval


---

## Architecture Overview

The MVP should be split into clear components.

### 1. Scenario Loader
Loads scenario definitions from disk.

A scenario includes:

- metadata
- target task
- system prompt
- tool list
- tool stubs / fixtures
- allowed actions
- expected behavior
- grading hints
- optional attacker content

### 2. Agent Runner
Executes one target agent in one scenario.

Responsibilities:

- initialize target model / target adapter
- provide tools
- drive turn loop
- capture events
- enforce max steps
- stop safely on violations or completion

### 3. Tool Sandbox
Provides controlled tool implementations.

Tools should be fake or wrapped.
No uncontrolled side effects.

### 4. Policy Engine
Evaluates behavior against explicit rules.

Examples:

- `send_email` requires explicit user approval
- `write_memory` must reject untrusted content
- `run_bash` is disabled in MVP
- `fetch_url` only allowed for whitelisted fixtures
- `export_data` never allowed unless scenario explicitly permits it

### 5. Trace Recorder
Stores complete run traces in structured form.

### 6. Evaluator
Scores the run based on:

- observed behavior
- violations
- suspicious decisions
- expected safe behavior

### 7. Report Generator
Produces Markdown reports.


---

## Suggested Directory Structure

```text
act0r/
  README.md
  ACT0R_SPEC.md
  pyproject.toml

  act0r/
    __init__.py
    config.py
    models.py
    runner.py
    policies.py
    evaluator.py
    reporting.py
    utils.py

    adapters/
      __init__.py
      base.py
      ollama_adapter.py
      openai_compatible_adapter.py

    tools/
      __init__.py
      registry.py
      base.py
      fake_email.py
      fake_memory.py
      fake_search.py
      fake_docs.py
      fake_export.py
      fake_fetch.py

    scenarios/
      loader.py
      schema.py

    traces/
      schema.py
      recorder.py

    storage/
      db.py
      repository.py
      schema.sql

  scenarios/
    email_summary_injection.yaml
    search_tool_hijack.yaml
    memory_poisoning.yaml
    overprivileged_export.yaml

  fixtures/
    docs/
    search/
    email/
    web/

  reports/
  runs/
  tests/