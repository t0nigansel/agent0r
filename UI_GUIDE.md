

# UI_GUIDE.md

## Purpose

This file defines the UI direction for `act0r`.

It exists so coding agents can build the interface with high autonomy while keeping the visual language and interaction model consistent.

`act0r` should look and feel like a sibling of `prompt0r`.
It should not feel like a different product.

The UI should serve operators who want to:
- choose targets
- choose scenarios
- launch runs
- inspect traces
- inspect violations
- inspect reports
- compare outcomes mentally and quickly

The interface should optimize for **clarity**, **speed**, and **technical trust**.


---

## Product Feel

The product should feel like:

- a serious engineering tool
- a security testing console
- a calm dark operator workspace
- compact and efficient
- technical but readable
- modern but not flashy

It should **not** feel like:

- a marketing site
- a playful dashboard
- a consumer app
- a design showcase
- a glossy SaaS landing page
- an over-animated analytics tool

The visual tone should communicate:

- control
- precision
- discipline
- observability
- safety analysis


---

## Primary Design Principle

**Mirror `prompt0r` wherever reasonable.**

When a design decision is unclear, prefer consistency with `prompt0r` over inventing a new pattern.

The goal is not originality.
The goal is family resemblance.


---

## Core UX Principle

The main workflow is:

1. select a target
2. select a scenario
3. run the test
4. inspect what happened
5. inspect violations and verdict
6. open or download the report

The UI must support this workflow with as little friction as possible.

The UI is not the product center of gravity.
The engine is.
The UI should expose the engine clearly.


---

## Layout Model

Use a layout similar to `prompt0r`.

### Global structure
- left sidebar
- main content area
- optional top utility bar if needed
- content-first screens
- minimal chrome

### Sidebar behavior
The left sidebar should contain the main navigation.
It should be stable and predictable.
It should not constantly change shape.

Primary sidebar sections:
- Targets
- Scenarios
- Runs
- Reports / Analysis
- Settings (optional, only if useful)

The sidebar should prioritize readability and fast switching.

### Main panel behavior
The main panel should be designed around:
- tables
- lists
- detail views
- trace inspection
- Markdown report rendering

Keep screens shallow.
Avoid deeply nested navigation.


---

## Density and Spacing

The interface should be **compact**, but not cramped.

### Good density
- enough rows visible at once
- enough information per screen
- small but readable controls
- reduced whitespace compared to marketing UIs

### Avoid
- huge cards
- oversized buttons
- overly spacious layouts
- excessive gutters
- giant empty margins

Spacing should feel deliberate and technical.


---

## Typography

Typography should feel calm, technical, and easy to scan.

### Typography rules
- prioritize readability over personality
- use a clean sans-serif for UI text
- use a monospaced font where code-like or trace-like data benefits from it
- keep font scale restrained
- avoid oversized headings
- use clear hierarchy, not dramatic hierarchy

### Suggested usage
- page titles: modest, not huge
- section titles: clear and consistent
- metadata labels: smaller and quieter
- trace/event content: monospaced where appropriate
- tables: compact, highly legible

The UI should not shout.
It should inform.


---

## Color Direction

The interface should use a **dark theme**.

### Tone
- deep dark background
- slightly raised panels
- subtle borders
- muted neutral text
- restrained accent color usage

### Color behavior
Use color primarily for:
- severity
- status
- active selection
- important actions
- success / warning / failure signals

Do not use many decorative colors.
Do not rely on gradients for identity.
Do not make the app look playful.

### Severity/status mapping
The exact palette can follow `prompt0r`, but these meanings should exist:
- neutral / inactive
- running / analyzing
- pass / success
- warning
- fail
- critical fail / dangerous
- blocked

These states must be visually easy to distinguish.


---

## Visual Style

### The style should be
- dark
- crisp
- flat to slightly elevated
- low-noise
- minimally ornamented
- border-driven rather than decoration-driven

### The style should not be
- glassy
- neon-heavy
- skeuomorphic
- cartoonish
- heavily rounded and soft
- loaded with shadows everywhere

Subtle depth is fine.
Heavy decorative styling is not.


---

## Component Philosophy

Components should be:
- reusable
- boring in a good way
- easy to scan
- easy to extend
- consistent across screens

The UI should prefer a small number of stable component patterns.

Use these patterns repeatedly:
- table
- list row
- detail section
- badge
- small action button
- panel
- tab strip if needed
- code/trace block
- Markdown viewer

Avoid inventing custom visual patterns for each screen.


---

## Buttons and Actions

Buttons should be practical.

### Preferred behavior
- compact size
- clear label
- small visual hierarchy differences
- destructive actions clearly distinct
- primary action obvious, but not oversized

### Avoid
- giant CTA buttons
- decorative icon-only actions without tooltip or meaning
- excessive button styles

Common actions likely needed:
- Run
- Analyze
- View
- Open Report
- Download Report
- Retry
- Filter
- Search

These should feel operator-oriented, not consumer-app-like.


---

## Tables

Tables are a core UI element.

The app will likely live or die by table quality.

### Tables should be
- compact
- sortable if useful
- easy to scan
- aligned cleanly
- capable of showing status and severity at a glance

### Typical table columns
For runs:
- status
- target
- scenario
- started
- finished
- verdict
- report state
- actions

For scenarios:
- id
- name
- category
- risk focus
- expected behavior summary

For targets:
- name
- type
- adapter
- availability
- last used

### Table rules
- avoid very tall rows
- use truncation thoughtfully
- allow opening detail view from a row
- use badges for compact state display


---

## Badges and Status Chips

Badges are important for fast scanning.

Use small, consistent badges for:
- verdict
- severity
- run status
- tool risk
- trust level
- blocked / allowed

Badges should be legible and restrained.
Avoid giant pill designs.


---

## Panels and Sections

Use panels to group related information.

Examples:
- run metadata
- scenario summary
- tool calls
- violations
- scores
- rendered report

Panels should:
- have consistent padding
- use subtle separation from background
- not feel like floating marketing cards
- stack predictably


---

## Icons

Use icons sparingly and functionally.

Icons should support meaning, not create it.

Good icon uses:
- run/play
- report/document
- warning
- success/fail
- tool/action
- settings
- search/filter

Avoid icon clutter.
Do not rely on icons alone to communicate critical state.


---

## Screen Definitions

### 1. Targets View
Purpose:
- show available targets
- indicate configuration state
- allow selection for a run

Should include:
- compact target list
- target type / adapter info
- availability / configuration state
- action to use target for a run

### 2. Scenarios View
Purpose:
- show available scenarios
- communicate risk type quickly
- allow quick selection for run execution

Should include:
- scenario list/table
- category
- summary
- risk focus
- expected behavior excerpt

### 3. Runs View
Purpose:
- show previous and current runs
- make status and verdict obvious
- allow fast access to details and reports

Should include:
- run history table
- filters if needed
- actions such as view, analyze, open report, download

### 4. Run Detail View
Purpose:
- show exactly what happened in one run
- help the operator inspect safety-relevant behavior

Should include:
- run metadata
- scenario summary
- target info
- event timeline
- tool calls
- violations
- scores
- final verdict
- report link or embedded report section

### 5. Report View
Purpose:
- render the Markdown report clearly
- support reading and export

Should include:
- rendered Markdown
- metadata header
- download/export action

### 6. Optional Analysis View
Purpose:
- provide a focused summary across results

This is optional for MVP.
If implemented, keep it restrained.
Do not build a massive analytics dashboard before the core workflow is solid.


---

## Run Detail View Priorities

This is likely the most important screen.

The operator should be able to answer quickly:
- what was tested?
- what should have happened?
- what actually happened?
- which tools were called?
- what was blocked?
- what violated policy?
- what is the verdict?
- where is the evidence?

That means this screen should emphasize:
- chronology
- evidence
- violations
- verdict clarity

It should not bury the critical information.


---

## Trace Presentation

Trace data should be readable.

### Trace rules
- chronological order
- stable timestamps or step indexes
- event type clearly visible
- actor visible where relevant
- tool call and tool result visually distinguishable
- policy decisions clearly marked
- violations highly visible

Use monospaced text where it helps.
Do not dump raw JSON as the primary view unless explicitly needed.

Raw structured data can exist behind an expandable section.


---

## Markdown Report Rendering

The report renderer should feel native to the app.

### Rendering rules
- readable line length
- clear headings
- clean tables
- code blocks styled consistently with the dark theme
- minimal visual noise

The report view should feel like part of the product, not like a raw browser document.


---

## Interaction Style

Interactions should be crisp and unsurprising.

### Preferred interaction qualities
- fast feedback
- minimal modal usage
- predictable navigation
- sensible defaults
- no excessive animation
- no distracting transitions

### Avoid
- wizard-heavy flows
- buried critical actions
- multi-step friction for simple tasks
- flashy state changes

The UI should help an operator stay mentally focused on the run data.


---

## Empty States

Empty states should be useful and minimal.

Examples:
- no runs yet
- no reports generated yet
- no scenarios configured
- no targets available

Each empty state should:
- explain what is missing
- suggest the next useful action
- avoid cute illustrations or jokes


---

## Error States

Error states should be calm and precise.

Show:
- what failed
- where it failed
- whether the run can be retried
- enough detail to debug

Avoid vague wording like:
- something went wrong
- unknown error

Prefer actionable, technical messages.


---

## Responsiveness

Desktop-first is acceptable for MVP.

The primary target is a developer or operator on a laptop or desktop.

### Priorities
- good desktop layout
- usable medium-width layout
- no need to optimize heavily for mobile in MVP

If tradeoffs are necessary, prioritize desktop operator workflow.


---

## Accessibility Basics

Even for MVP, basic accessibility matters.

Include:
- sufficient contrast
- visible keyboard focus states
- readable font sizes
- non-color-only status communication
- tooltips or labels for ambiguous controls

This does not need to become an accessibility overhaul at MVP stage, but avoid obvious mistakes.


---

## Suggested Information Hierarchy

For most screens, use this hierarchy:

1. page purpose
2. key actions
3. primary dataset or detail view
4. secondary metadata
5. deep/raw detail only when needed

The UI should surface important decisions and evidence first.
Raw exhaust comes later.


---

## Animation Guidance

Keep animation minimal.

Allowed:
- subtle hover feedback
- subtle selection feedback
- simple loading indicators
- lightweight panel transitions if needed

Avoid:
- dramatic motion
- animated charts for no reason
- bouncing elements
- excessive shimmer effects

`act0r` should feel disciplined.


---

## Implementation Guidance For Coding Agents

When building the UI:

- reuse patterns aggressively
- prefer small composable components
- keep styling tokens centralized
- keep status color rules consistent
- do not add decorative UI just because space exists
- choose compact defaults
- mirror `prompt0r` patterns where known
- keep the run inspection workflow central

When uncertain:
- choose the simpler layout
- choose the denser layout
- choose the more technical-looking layout
- choose the option that feels more like an internal operator tool


---

## MVP UI Checklist

The MVP UI should provide at least:

- a stable left sidebar
- a runs list
- a run detail screen
- a scenarios list
- a targets list
- a report view
- compact tables
- status badges
- severity badges
- readable trace presentation
- a consistent dark theme

If those are done well, the UI is good enough for MVP.


---

## Final Instruction

The UI should feel like `prompt0r`’s sibling.

Not identical.
But clearly related.

When in doubt, reduce ornament, increase clarity, keep the layout compact, and prioritize the operator’s ability to inspect a run quickly.