from __future__ import annotations

import json
from typing import Any
from typing import List

from .models import (
    MultiAgentSession,
    WorkflowAnalysis,
    WorkflowFinding,
    WorkflowSeverity,
)

REQUIRED_POLICY_KEYS = [
    "trust_boundary",
    "high_risk_approval_required",
]


def _stable_value(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


class MultiAgentWorkflowAnalyzer:
    def analyze(self, session: MultiAgentSession) -> WorkflowAnalysis:
        findings: List[WorkflowFinding] = []

        for index, handoff in enumerate(session.handoffs):
            parent = session.agents.get(handoff.from_agent_id)
            child = session.agents.get(handoff.to_agent_id)

            if parent is None or child is None:
                findings.append(
                    WorkflowFinding(
                        check_id="MA-000",
                        severity=WorkflowSeverity.HIGH,
                        message="Handoff references unknown agent id.",
                        handoff_index=index,
                    )
                )
                continue

            if not handoff.task.strip():
                findings.append(
                    WorkflowFinding(
                        check_id="MA-001",
                        severity=WorkflowSeverity.MEDIUM,
                        message="Handoff task is empty or unclear.",
                        handoff_index=index,
                    )
                )

            parent_privileges = set(parent.privileges)
            granted_privileges = set(handoff.granted_privileges)
            requested_privileges = set(handoff.requested_privileges)
            child_privileges = set(child.privileges)

            escalated_grants = sorted(granted_privileges - parent_privileges)
            if escalated_grants:
                findings.append(
                    WorkflowFinding(
                        check_id="MA-002",
                        severity=WorkflowSeverity.HIGH,
                        message="Granted privileges exceed parent scope: {}".format(
                            ", ".join(escalated_grants)
                        ),
                        handoff_index=index,
                    )
                )

            implicit_child_privileges = sorted(child_privileges - granted_privileges)
            if implicit_child_privileges:
                findings.append(
                    WorkflowFinding(
                        check_id="MA-002",
                        severity=WorkflowSeverity.HIGH,
                        message="Child agent has undeclared privileges: {}".format(
                            ", ".join(implicit_child_privileges)
                        ),
                        handoff_index=index,
                    )
                )

            unexpected_requested = sorted(requested_privileges - parent_privileges)
            if unexpected_requested:
                findings.append(
                    WorkflowFinding(
                        check_id="MA-002",
                        severity=WorkflowSeverity.MEDIUM,
                        message="Requested privileges exceed parent scope: {}".format(
                            ", ".join(unexpected_requested)
                        ),
                        handoff_index=index,
                    )
                )

            missing_policy = [
                key for key in REQUIRED_POLICY_KEYS if key not in handoff.propagated_policy
            ]
            if missing_policy:
                findings.append(
                    WorkflowFinding(
                        check_id="MA-003",
                        severity=WorkflowSeverity.MEDIUM,
                        message="Missing propagated policy keys: {}".format(
                            ", ".join(missing_policy)
                        ),
                        handoff_index=index,
                    )
                )

            for key in REQUIRED_POLICY_KEYS:
                if key in parent.policy_context and key in handoff.propagated_policy:
                    expected = parent.policy_context[key]
                    got = handoff.propagated_policy[key]
                    if expected != got:
                        findings.append(
                            WorkflowFinding(
                                check_id="MA-003",
                                severity=WorkflowSeverity.HIGH,
                                message=(
                                    "Propagated policy mismatch for {}: expected {} got {}".format(
                                        key,
                                        _stable_value(expected),
                                        _stable_value(got),
                                    )
                                ),
                                handoff_index=index,
                            )
                        )

                if key in handoff.propagated_policy and key in child.policy_context:
                    expected = handoff.propagated_policy[key]
                    got = child.policy_context[key]
                    if expected != got:
                        findings.append(
                            WorkflowFinding(
                                check_id="MA-003",
                                severity=WorkflowSeverity.MEDIUM,
                                message=(
                                    "Child policy context mismatch for {}: expected {} got {}".format(
                                        key,
                                        _stable_value(expected),
                                        _stable_value(got),
                                    )
                                ),
                                handoff_index=index,
                            )
                        )

        findings.sort(key=lambda item: (item.handoff_index, item.check_id, item.message))
        return WorkflowAnalysis(session_id=session.session_id, findings=findings)
