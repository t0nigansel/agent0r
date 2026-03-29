from __future__ import annotations

from typing import List

from act0r.adapters import AgentAdapter, AdapterRequest, AdapterResponse, AdapterRuntimeError, AdapterToolCall
from act0r.runner import AgentRunner, RunStatus
from act0r.scenarios import load_scenario
from act0r.tools import create_default_tool_registry
from act0r.trace import EventType


class SequenceAdapter(AgentAdapter):
    def __init__(self, responses: List[AdapterResponse]) -> None:
        self.responses = list(responses)

    def generate(self, request: AdapterRequest) -> AdapterResponse:
        if not self.responses:
            return AdapterResponse(assistant_text="", is_final=True)
        return self.responses.pop(0)


class LoopingAdapter(AgentAdapter):
    def generate(self, request: AdapterRequest) -> AdapterResponse:
        return AdapterResponse(assistant_text="thinking", is_final=False)


class FailingAdapter(AgentAdapter):
    def generate(self, request: AdapterRequest) -> AdapterResponse:
        raise AdapterRuntimeError("simulated adapter failure")



def test_runner_completes_and_records_tool_events() -> None:
    scenario = load_scenario("scenarios/mvp/SCN-001_benign_email_summary.yaml")
    adapter = SequenceAdapter(
        responses=[
            AdapterResponse(
                assistant_text="I will read the email",
                tool_calls=[AdapterToolCall(name="read_email", arguments={})],
                is_final=False,
            ),
            AdapterResponse(
                assistant_text="Summary: blockers and updates captured.",
                tool_calls=[],
                is_final=True,
            ),
        ]
    )

    runner = AgentRunner(adapter=adapter, tool_registry=create_default_tool_registry(), max_steps=4)
    result = runner.run(scenario, run_id="run-phase4-complete")

    event_types = [event.event_type for event in result.trace.events]

    assert result.status == RunStatus.COMPLETED
    assert result.evaluation is not None
    assert result.stop_reason == "adapter_signaled_completion"
    assert EventType.POLICY_DECISION in event_types
    assert EventType.TOOL_CALL_REQUESTED in event_types
    assert EventType.TOOL_CALL_EXECUTED in event_types
    assert EventType.TOOL_RESULT in event_types
    assert event_types[-1] == EventType.RUN_COMPLETED


def test_runner_stops_on_blocked_high_risk_tool_action() -> None:
    scenario = load_scenario("scenarios/mvp/SCN-005_unauthorized_export_attempt.yaml")
    adapter = SequenceAdapter(
        responses=[
            AdapterResponse(
                assistant_text="Attempting export",
                tool_calls=[
                    AdapterToolCall(name="export_data", arguments={"dataset_name": "customer_snapshot"})
                ],
                is_final=False,
            )
        ]
    )

    runner = AgentRunner(adapter=adapter, tool_registry=create_default_tool_registry(), max_steps=4)
    result = runner.run(scenario, run_id="run-phase4-blocked")

    assert result.status == RunStatus.STOPPED_BLOCKED_CRITICAL_ACTION
    assert result.evaluation is not None
    assert result.stop_reason == "policy_blocked_action"
    assert result.trace.events[-1].event_type == EventType.RUN_STOPPED
    assert result.trace.events[-1].payload["reason"] == "policy_blocked_action"


def test_runner_stops_when_max_steps_reached() -> None:
    scenario = load_scenario("scenarios/mvp/SCN-001_benign_email_summary.yaml")
    runner = AgentRunner(
        adapter=LoopingAdapter(),
        tool_registry=create_default_tool_registry(),
        max_steps=2,
    )

    result = runner.run(scenario, run_id="run-phase4-max-steps")

    assert result.status == RunStatus.STOPPED_MAX_STEPS
    assert result.evaluation is not None
    assert result.stop_reason == "max_steps_exceeded"
    assert result.trace.events[-1].payload["reason"] == "max_steps_exceeded"


def test_runner_stops_on_adapter_error() -> None:
    scenario = load_scenario("scenarios/mvp/SCN-001_benign_email_summary.yaml")
    runner = AgentRunner(
        adapter=FailingAdapter(),
        tool_registry=create_default_tool_registry(),
        max_steps=2,
    )

    result = runner.run(scenario, run_id="run-phase4-adapter-error")

    assert result.status == RunStatus.STOPPED_ADAPTER_ERROR
    assert result.evaluation is not None
    assert result.stop_reason == "adapter_error"
    assert result.trace.events[-1].event_type == EventType.RUN_STOPPED
    assert result.trace.events[-1].payload["reason"] == "adapter_error"
