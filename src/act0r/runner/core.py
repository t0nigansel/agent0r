from __future__ import annotations

import json
from uuid import uuid4
from typing import Optional

from act0r.adapters import AdapterMessage, AdapterRequest, AgentAdapter
from act0r.evaluation import DeterministicEvaluator
from act0r.policy import PolicyEngine, PolicyEvaluation, PolicyOutcome
from act0r.scenarios.models import LoadedScenario
from act0r.tools import (
    RiskLevel,
    ToolExecutionContext,
    ToolRegistry,
    ToolRegistryError,
    TrustLevel,
)
from act0r.trace import EventType, TraceRecorder

from .models import RunResult, RunStatus


class AgentRunner:
    def __init__(
        self,
        *,
        adapter: AgentAdapter,
        tool_registry: ToolRegistry,
        evaluator: Optional[DeterministicEvaluator] = None,
        max_steps: int = 8,
    ) -> None:
        if max_steps <= 0:
            raise ValueError("max_steps must be greater than zero")

        self.adapter = adapter
        self.tool_registry = tool_registry
        self.evaluator = evaluator or DeterministicEvaluator()
        self.max_steps = max_steps

    def run(
        self, loaded_scenario: LoadedScenario, *, run_id: Optional[str] = None
    ) -> RunResult:
        active_run_id = run_id or "run-{}".format(uuid4().hex[:12])
        recorder = TraceRecorder(active_run_id)
        scenario = loaded_scenario.scenario

        recorder.record(EventType.SYSTEM_PROMPT, {"text": scenario.system_prompt})
        recorder.record(EventType.USER_TASK, {"text": scenario.user_task})

        messages = [
            AdapterMessage(role="system", content=scenario.system_prompt),
            AdapterMessage(role="user", content=scenario.user_task),
        ]

        available_tools = self.tool_registry.resolve_for_loaded_scenario(loaded_scenario)
        fixture_values = {
            name: fixture.content for name, fixture in loaded_scenario.fixtures.items()
        }
        tool_context = ToolExecutionContext(
            scenario_id=scenario.id,
            fixtures=fixture_values,
        )
        policy_engine = PolicyEngine(scenario)
        recent_untrusted_output_seen = False

        final_text = None

        def build_result(
            status: RunStatus, steps_executed: int, *, stop_reason: Optional[str] = None
        ) -> RunResult:
            trace = recorder.to_trace()
            return RunResult(
                run_id=active_run_id,
                scenario_id=scenario.id,
                status=status,
                steps_executed=steps_executed,
                trace=trace,
                evaluation=self.evaluator.evaluate(trace),
                stop_reason=stop_reason,
                final_response=final_text,
            )

        for step in range(self.max_steps):
            request = AdapterRequest(
                messages=messages,
                available_tools=[tool.spec for tool in available_tools],
                step_index=step,
            )

            try:
                response = self.adapter.generate(request)
            except Exception as exc:
                recorder.record(
                    EventType.RUN_STOPPED,
                    {
                        "reason": "adapter_error",
                        "error": str(exc),
                    },
                )
                return build_result(
                    RunStatus.STOPPED_ADAPTER_ERROR,
                    step,
                    stop_reason="adapter_error",
                )

            assistant_event = recorder.record(
                EventType.ASSISTANT_RESPONSE,
                {
                    "text": response.assistant_text,
                    "tool_calls": [call.model_dump(mode="json") for call in response.tool_calls],
                    "is_final": response.is_final,
                },
            )
            messages.append(AdapterMessage(role="assistant", content=response.assistant_text))

            if response.assistant_text:
                final_text = response.assistant_text

            assistant_policy = policy_engine.evaluate_after_assistant(
                assistant_text=response.assistant_text,
                tool_calls=response.tool_calls,
                user_task=scenario.user_task,
                recent_untrusted_output_seen=recent_untrusted_output_seen,
                evidence_event_indexes=[assistant_event.step_index],
            )
            assistant_blocking = _record_policy_evaluation(recorder, assistant_policy)
            if assistant_blocking is not None:
                recorder.record(
                    EventType.RUN_STOPPED,
                    {
                        "reason": "policy_violation",
                        "rule_id": assistant_blocking.rule_id.value,
                        "outcome": assistant_blocking.outcome.value,
                    },
                )
                return build_result(
                    RunStatus.STOPPED_BLOCKED_CRITICAL_ACTION,
                    step + 1,
                    stop_reason="policy_violation",
                )

            for call in response.tool_calls:
                tool_request_event = recorder.record(
                    EventType.TOOL_CALL_REQUESTED,
                    {
                        "tool_name": call.name,
                        "arguments": call.arguments,
                    },
                )

                try:
                    tool = self.tool_registry.get(call.name)
                except ToolRegistryError as exc:
                    recorder.record(
                        EventType.RUN_STOPPED,
                        {
                            "reason": "adapter_error",
                            "error": str(exc),
                        },
                    )
                    return build_result(
                        RunStatus.STOPPED_ADAPTER_ERROR,
                        step + 1,
                        stop_reason="unknown_tool",
                    )

                pre_tool_policy = policy_engine.evaluate_before_tool(
                    tool_spec=tool.spec,
                    arguments=call.arguments,
                    evidence_event_indexes=[tool_request_event.step_index],
                )
                pre_tool_blocking = _record_policy_evaluation(recorder, pre_tool_policy)
                if pre_tool_blocking is not None:
                    recorder.record(
                        EventType.RUN_STOPPED,
                        {
                            "reason": "policy_blocked_action",
                            "rule_id": pre_tool_blocking.rule_id.value,
                            "outcome": pre_tool_blocking.outcome.value,
                            "tool_name": call.name,
                        },
                    )
                    return build_result(
                        RunStatus.STOPPED_BLOCKED_CRITICAL_ACTION,
                        step + 1,
                        stop_reason="policy_blocked_action",
                    )

                recorder.record(
                    EventType.TOOL_CALL_EXECUTED,
                    {
                        "tool_name": call.name,
                    },
                )

                result = tool.execute(arguments=call.arguments, context=tool_context)

                recorder.record(
                    EventType.TOOL_RESULT,
                    result.model_dump(mode="json"),
                )

                if result.trust_level == TrustLevel.UNTRUSTED:
                    recent_untrusted_output_seen = True

                messages.append(
                    AdapterMessage(
                        role="tool",
                        content=_serialize_tool_output(result.output),
                    )
                )

                if result.blocked and result.risk_level == RiskLevel.HIGH:
                    recorder.record(
                        EventType.RUN_STOPPED,
                        {
                            "reason": "blocked_critical_action",
                            "tool_name": result.tool_name,
                        },
                    )
                    return build_result(
                        RunStatus.STOPPED_BLOCKED_CRITICAL_ACTION,
                        step + 1,
                        stop_reason="blocked_critical_action",
                    )

            if response.is_final:
                recorder.record(
                    EventType.RUN_COMPLETED,
                    {"reason": "adapter_signaled_completion"},
                )
                return build_result(
                    RunStatus.COMPLETED,
                    step + 1,
                    stop_reason="adapter_signaled_completion",
                )

        recorder.record(
            EventType.RUN_STOPPED,
            {"reason": "max_steps_exceeded", "max_steps": self.max_steps},
        )
        return build_result(
            RunStatus.STOPPED_MAX_STEPS,
            self.max_steps,
            stop_reason="max_steps_exceeded",
        )


def _serialize_tool_output(output: object) -> str:
    try:
        return json.dumps(output, sort_keys=True)
    except TypeError:
        return str(output)


def _record_policy_evaluation(
    recorder: TraceRecorder, evaluation: PolicyEvaluation
):
    for decision in evaluation.decisions:
        recorder.record(
            EventType.POLICY_DECISION,
            decision.model_dump(mode="json"),
        )

    for violation in evaluation.violations:
        recorder.record(
            EventType.VIOLATION_DETECTED,
            violation.model_dump(mode="json"),
        )

    for decision in evaluation.decisions:
        if decision.outcome in {PolicyOutcome.BLOCK, PolicyOutcome.DENY}:
            return decision

    return None
