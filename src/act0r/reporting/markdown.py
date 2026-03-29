from __future__ import annotations

from pathlib import Path
from typing import List

from act0r.runner import RunResult
from act0r.scenarios.models import LoadedScenario
from act0r.trace import EventType


class MarkdownReportGenerator:
    def render(self, run_result: RunResult, loaded_scenario: LoadedScenario) -> str:
        scenario = loaded_scenario.scenario
        trace = run_result.trace

        tool_calls = [
            event.payload
            for event in trace.events
            if event.event_type == EventType.TOOL_CALL_REQUESTED
        ]
        violations = [
            event.payload
            for event in trace.events
            if event.event_type == EventType.VIOLATION_DETECTED
        ]
        assistant_messages = [
            event.payload.get("text", "")
            for event in trace.events
            if event.event_type == EventType.ASSISTANT_RESPONSE
        ]

        lines: List[str] = []
        lines.append("# act0r Run Report")
        lines.append("")

        lines.append("## Run metadata")
        lines.append("| field | value |")
        lines.append("| --- | --- |")
        lines.append("| run_id | {} |".format(run_result.run_id))
        lines.append("| scenario_id | {} |".format(run_result.scenario_id))
        lines.append("| status | {} |".format(run_result.status.value))
        lines.append("| steps_executed | {} |".format(run_result.steps_executed))
        lines.append("| verdict | {} |".format(run_result.evaluation.verdict.value if run_result.evaluation else "n/a"))
        lines.append("")

        lines.append("## Scenario summary")
        lines.append("- id: {}".format(scenario.id))
        lines.append("- title: {}".format(scenario.title))
        lines.append("- category: {}".format(scenario.category))
        lines.append("- security_focus: {}".format(", ".join(scenario.security_focus) if scenario.security_focus else "n/a"))
        lines.append("")

        lines.append("## Expected safe behavior")
        if scenario.policy_expectations:
            for expectation in scenario.policy_expectations:
                lines.append(
                    "- {} {}: {}".format(
                        expectation.rule_id,
                        expectation.outcome,
                        expectation.description,
                    )
                )
        else:
            lines.append("- no explicit policy expectations declared")
        lines.append("")

        lines.append("## Observed behavior")
        lines.append("- assistant_responses: {}".format(len(assistant_messages)))
        if assistant_messages:
            lines.append("- final_assistant_response: {}".format(assistant_messages[-1]))
        else:
            lines.append("- final_assistant_response: n/a")
        lines.append("- trace_events: {}".format(len(trace.events)))
        lines.append("")

        lines.append("## Tool calls")
        if tool_calls:
            lines.append("| tool | arguments |")
            lines.append("| --- | --- |")
            for call in tool_calls:
                lines.append(
                    "| {} | {} |".format(
                        call.get("tool_name", "unknown"),
                        _inline_dict(call.get("arguments", {})),
                    )
                )
        else:
            lines.append("- no tool calls recorded")
        lines.append("")

        lines.append("## Violations")
        if violations:
            lines.append("| rule | severity | action | message |")
            lines.append("| --- | --- | --- | --- |")
            for violation in violations:
                lines.append(
                    "| {} | {} | {} | {} |".format(
                        violation.get("rule_id", "n/a"),
                        violation.get("severity", "n/a"),
                        violation.get("action", "n/a"),
                        violation.get("message", ""),
                    )
                )
        else:
            lines.append("- no violations detected")
        lines.append("")

        lines.append("## Evaluation scores")
        if run_result.evaluation:
            scores = run_result.evaluation.scores
            lines.append("| metric | score |")
            lines.append("| --- | --- |")
            lines.append("| goal_alignment | {} |".format(scores.goal_alignment))
            lines.append("| tool_safety | {} |".format(scores.tool_safety))
            lines.append("| memory_safety | {} |".format(scores.memory_safety))
            lines.append("| data_exfiltration_resistance | {} |".format(scores.data_exfiltration_resistance))
            lines.append("| prompt_injection_resistance | {} |".format(scores.prompt_injection_resistance))
            lines.append("| overall_score | {} |".format(scores.overall_score))
        else:
            lines.append("- evaluation unavailable")
        lines.append("")

        lines.append("## Final assessment")
        if run_result.evaluation:
            lines.append("- verdict: {}".format(run_result.evaluation.verdict.value))
            if run_result.evaluation.critical_failures:
                for failure in run_result.evaluation.critical_failures:
                    lines.append("- critical: {}".format(failure))
        else:
            lines.append("- verdict unavailable")
        lines.append("")

        lines.append("## Recommendations")
        lines.extend(_recommendations(run_result))
        lines.append("")

        return "\n".join(lines)

    def generate(
        self,
        run_result: RunResult,
        loaded_scenario: LoadedScenario,
        output_dir: Path,
    ) -> Path:
        output_path = output_dir.expanduser().resolve()
        output_path.mkdir(parents=True, exist_ok=True)

        report_path = output_path / "{}.md".format(run_result.run_id)
        report_path.write_text(
            self.render(run_result=run_result, loaded_scenario=loaded_scenario),
            encoding="utf-8",
        )
        return report_path


def _inline_dict(value) -> str:
    if not value:
        return "{}"
    if not isinstance(value, dict):
        return str(value)
    pairs = ["{}={}".format(key, value[key]) for key in sorted(value)]
    return "{" + ", ".join(pairs) + "}"


def _recommendations(run_result: RunResult) -> List[str]:
    if run_result.evaluation is None:
        return ["- generate evaluation before producing recommendations"]

    verdict = run_result.evaluation.verdict.value
    if verdict == "PASS":
        return ["- maintain current controls and expand scenario coverage"]
    if verdict == "PASS_WITH_WARNINGS":
        return ["- investigate warnings and tighten high-risk action gating"]
    if verdict == "FAIL":
        return ["- address policy gaps before promoting this agent configuration"]
    return ["- block deployment until critical failures are resolved"]
