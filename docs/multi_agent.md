# Multi-Agent Workflow Checks

`act0r.multi_agent` provides deterministic checks for parent/sub-agent handoffs.

## Models

- `AgentNode`: agent identity, role, granted privilege set, and policy context.
- `HandoffRecord`: parent -> child transfer metadata, requested/granted privileges, and propagated policy.
- `MultiAgentSession`: map of agents plus ordered handoff records.
- `WorkflowAnalysis`: ordered findings for the full session.

## Analyzer

Use `MultiAgentWorkflowAnalyzer.analyze(session)` to evaluate a handoff sequence.

Implemented checks:

- `MA-000`: handoff references unknown agent IDs.
- `MA-001`: handoff task is empty/unclear.
- `MA-002`: privilege escalation or undeclared child privileges.
- `MA-003`: missing or inconsistent policy propagation across parent/handoff/child.

The analyzer output is deterministic:

- findings are sorted by handoff index, check ID, and message
- mismatch values are serialized with stable JSON formatting
