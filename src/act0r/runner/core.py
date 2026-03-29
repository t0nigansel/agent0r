from __future__ import annotations

import json
from uuid import uuid4
from typing import Optional

from act0r.adapters import AdapterMessage, AdapterRequest, AgentAdapter
from act0r.scenarios.models import LoadedScenario
from act0r.tools import RiskLevel, ToolExecutionContext, ToolRegistry, ToolRegistryError
from act0r.trace import EventType, TraceRecorder

from .models import RunResult, RunStatus


class AgentRunner:
    def __init__(
        self,
        *,
        adapter: AgentAdapter,
        tool_registry: ToolRegistry,
        max_steps: int = 8,
    ) -> None:
        if max_steps <= 0:
            raise ValueError("max_steps must be greater than zero")

        self.adapter = adapter
        self.tool_registry = tool_registry
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

        final_text = None

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
                return RunResult(
                    run_id=active_run_id,
                    scenario_id=scenario.id,
                    status=RunStatus.STOPPED_ADAPTER_ERROR,
                    steps_executed=step,
                    trace=recorder.to_trace(),
                    final_response=final_text,
                )

            recorder.record(
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

            for call in response.tool_calls:
                recorder.record(
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
                    return RunResult(
                        run_id=active_run_id,
                        scenario_id=scenario.id,
                        status=RunStatus.STOPPED_ADAPTER_ERROR,
                        steps_executed=step + 1,
                        trace=recorder.to_trace(),
                        final_response=final_text,
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
                    return RunResult(
                        run_id=active_run_id,
                        scenario_id=scenario.id,
                        status=RunStatus.STOPPED_BLOCKED_CRITICAL_ACTION,
                        steps_executed=step + 1,
                        trace=recorder.to_trace(),
                        final_response=final_text,
                    )

            if response.is_final:
                recorder.record(
                    EventType.RUN_COMPLETED,
                    {"reason": "adapter_signaled_completion"},
                )
                return RunResult(
                    run_id=active_run_id,
                    scenario_id=scenario.id,
                    status=RunStatus.COMPLETED,
                    steps_executed=step + 1,
                    trace=recorder.to_trace(),
                    final_response=final_text,
                )

        recorder.record(
            EventType.RUN_STOPPED,
            {"reason": "max_steps_exceeded", "max_steps": self.max_steps},
        )
        return RunResult(
            run_id=active_run_id,
            scenario_id=scenario.id,
            status=RunStatus.STOPPED_MAX_STEPS,
            steps_executed=self.max_steps,
            trace=recorder.to_trace(),
            final_response=final_text,
        )


def _serialize_tool_output(output: object) -> str:
    try:
        return json.dumps(output, sort_keys=True)
    except TypeError:
        return str(output)
