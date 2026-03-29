from __future__ import annotations

from act0r.multi_agent import (
    AgentNode,
    AgentRole,
    HandoffRecord,
    MultiAgentSession,
    MultiAgentWorkflowAnalyzer,
)


def _base_agents():
    return {
        "parent": AgentNode(
            agent_id="parent",
            role=AgentRole.PARENT,
            privileges={"read_email", "search_docs", "read_doc"},
            policy_context={
                "trust_boundary": "untrusted-tools",
                "high_risk_approval_required": True,
            },
        ),
        "child": AgentNode(
            agent_id="child",
            role=AgentRole.SUB_AGENT,
            privileges={"read_email"},
            policy_context={
                "trust_boundary": "untrusted-tools",
                "high_risk_approval_required": True,
            },
        ),
    }


def test_multi_agent_handoff_passes_when_scope_and_policy_are_safe() -> None:
    session = MultiAgentSession(
        session_id="session-safe",
        agents=_base_agents(),
        handoffs=[
            HandoffRecord(
                from_agent_id="parent",
                to_agent_id="child",
                task="Summarize inbox content.",
                requested_privileges=["read_email"],
                granted_privileges=["read_email"],
                propagated_policy={
                    "trust_boundary": "untrusted-tools",
                    "high_risk_approval_required": True,
                },
            )
        ],
    )

    analysis = MultiAgentWorkflowAnalyzer().analyze(session)

    assert analysis.passed is True
    assert analysis.findings == []


def test_multi_agent_detects_privilege_escalation() -> None:
    agents = _base_agents()
    agents["child"] = agents["child"].model_copy(
        update={"privileges": {"read_email", "export_data"}}
    )

    session = MultiAgentSession(
        session_id="session-escalation",
        agents=agents,
        handoffs=[
            HandoffRecord(
                from_agent_id="parent",
                to_agent_id="child",
                task="Handle export.",
                requested_privileges=["export_data"],
                granted_privileges=["export_data"],
                propagated_policy={
                    "trust_boundary": "untrusted-tools",
                    "high_risk_approval_required": True,
                },
            )
        ],
    )

    analysis = MultiAgentWorkflowAnalyzer().analyze(session)
    ids = [finding.check_id for finding in analysis.findings]

    assert analysis.passed is False
    assert "MA-002" in ids


def test_multi_agent_detects_missing_policy_context_propagation() -> None:
    session = MultiAgentSession(
        session_id="session-policy-missing",
        agents=_base_agents(),
        handoffs=[
            HandoffRecord(
                from_agent_id="parent",
                to_agent_id="child",
                task="Summarize inbox safely.",
                requested_privileges=["read_email"],
                granted_privileges=["read_email"],
                propagated_policy={
                    "trust_boundary": "untrusted-tools",
                },
            )
        ],
    )

    analysis = MultiAgentWorkflowAnalyzer().analyze(session)

    assert analysis.passed is False
    assert any(item.check_id == "MA-003" for item in analysis.findings)


def test_multi_agent_detects_unknown_agent_in_handoff() -> None:
    session = MultiAgentSession(
        session_id="session-unknown-agent",
        agents=_base_agents(),
        handoffs=[
            HandoffRecord(
                from_agent_id="parent",
                to_agent_id="ghost-agent",
                task="Summarize inbox safely.",
                requested_privileges=["read_email"],
                granted_privileges=["read_email"],
                propagated_policy={
                    "trust_boundary": "untrusted-tools",
                    "high_risk_approval_required": True,
                },
            )
        ],
    )

    analysis = MultiAgentWorkflowAnalyzer().analyze(session)

    assert analysis.passed is False
    assert any(item.check_id == "MA-000" for item in analysis.findings)


def test_multi_agent_detects_parent_policy_value_mismatch() -> None:
    session = MultiAgentSession(
        session_id="session-parent-policy-mismatch",
        agents=_base_agents(),
        handoffs=[
            HandoffRecord(
                from_agent_id="parent",
                to_agent_id="child",
                task="Summarize inbox safely.",
                requested_privileges=["read_email"],
                granted_privileges=["read_email"],
                propagated_policy={
                    "trust_boundary": "trusted-only",
                    "high_risk_approval_required": True,
                },
            )
        ],
    )

    analysis = MultiAgentWorkflowAnalyzer().analyze(session)

    assert analysis.passed is False
    assert any(
        item.check_id == "MA-003" and "Propagated policy mismatch" in item.message
        for item in analysis.findings
    )


def test_multi_agent_detects_child_policy_context_mismatch() -> None:
    agents = _base_agents()
    agents["child"] = agents["child"].model_copy(
        update={
            "policy_context": {
                "trust_boundary": "trusted-only",
                "high_risk_approval_required": True,
            }
        }
    )

    session = MultiAgentSession(
        session_id="session-child-policy-mismatch",
        agents=agents,
        handoffs=[
            HandoffRecord(
                from_agent_id="parent",
                to_agent_id="child",
                task="Summarize inbox safely.",
                requested_privileges=["read_email"],
                granted_privileges=["read_email"],
                propagated_policy={
                    "trust_boundary": "untrusted-tools",
                    "high_risk_approval_required": True,
                },
            )
        ],
    )

    analysis = MultiAgentWorkflowAnalyzer().analyze(session)

    assert analysis.passed is False
    assert any(
        item.check_id == "MA-003" and "Child policy context mismatch" in item.message
        for item in analysis.findings
    )
