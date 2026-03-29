from __future__ import annotations

import argparse
import sys
from pathlib import Path
from uuid import uuid4

from act0r.adapters import AdapterRequest, AdapterResponse, AdapterToolCall, AgentAdapter
from act0r.reporting import MarkdownReportGenerator
from act0r.runner import AgentRunner
from act0r.scenarios import load_scenario, load_scenarios_from_directory
from act0r.storage import SQLiteStorage
from act0r.tools import create_default_tool_registry


class DeterministicCliAdapter(AgentAdapter):
    def generate(self, request: AdapterRequest) -> AdapterResponse:
        if request.step_index == 0 and request.available_tools:
            first_tool = request.available_tools[0]
            return AdapterResponse(
                assistant_text="Planning to call {}.".format(first_tool.name),
                tool_calls=[AdapterToolCall(name=first_tool.name, arguments={})],
                is_final=False,
            )
        return AdapterResponse(
            assistant_text="Run completed.",
            tool_calls=[],
            is_final=True,
        )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="act0r", description="act0r operator CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    list_parser = subparsers.add_parser("list-scenarios", help="List scenario files")
    list_parser.add_argument(
        "--scenario-dir",
        default="scenarios/mvp",
        help="Directory containing scenario YAML files",
    )

    run_parser = subparsers.add_parser("run", help="Run one scenario")
    run_parser.add_argument("--scenario", required=True, help="Scenario YAML file path")
    run_parser.add_argument("--db", default="data/act0r.sqlite", help="SQLite database path")
    run_parser.add_argument("--report-dir", default="reports", help="Report output directory")
    run_parser.add_argument("--max-steps", type=int, default=8, help="Max runner steps")
    run_parser.add_argument("--run-id", default=None, help="Optional explicit run id")

    run_all_parser = subparsers.add_parser("run-all", help="Run all scenarios in a directory")
    run_all_parser.add_argument("--scenario-dir", default="scenarios/mvp", help="Scenario directory")
    run_all_parser.add_argument("--db", default="data/act0r.sqlite", help="SQLite database path")
    run_all_parser.add_argument("--report-dir", default="reports", help="Report output directory")
    run_all_parser.add_argument("--max-steps", type=int, default=8, help="Max runner steps")

    report_parser = subparsers.add_parser("report", help="Regenerate report from stored run")
    report_parser.add_argument("--run-id", required=True, help="Run id")
    report_parser.add_argument("--db", default="data/act0r.sqlite", help="SQLite database path")
    report_parser.add_argument("--output-dir", default="reports", help="Report output directory")

    return parser


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        if args.command == "list-scenarios":
            return _cmd_list_scenarios(args)
        if args.command == "run":
            return _cmd_run(args)
        if args.command == "run-all":
            return _cmd_run_all(args)
        if args.command == "report":
            return _cmd_report(args)
    except Exception as exc:
        print("error: {}".format(exc), file=sys.stderr)
        return 1

    return 1


def _cmd_list_scenarios(args) -> int:
    loaded = load_scenarios_from_directory(args.scenario_dir)
    for item in loaded:
        scenario = item.scenario
        print("{}\t{}\t{}".format(scenario.id, scenario.title, scenario.category))
    return 0


def _cmd_run(args) -> int:
    loaded = load_scenario(args.scenario)
    adapter = DeterministicCliAdapter()
    runner = AgentRunner(
        adapter=adapter,
        tool_registry=create_default_tool_registry(),
        max_steps=args.max_steps,
    )

    run_id = args.run_id or "cli-{}".format(uuid4().hex[:10])
    run_result = runner.run(loaded, run_id=run_id)

    storage = SQLiteStorage(Path(args.db))
    try:
        storage.persist_full_run(loaded, run_result)
    finally:
        storage.close()

    report_path = MarkdownReportGenerator().generate(
        run_result,
        loaded,
        Path(args.report_dir),
    )

    print(
        "run_id={} scenario={} status={} verdict={} score={} report={}".format(
            run_result.run_id,
            run_result.scenario_id,
            run_result.status.value,
            run_result.evaluation.verdict.value if run_result.evaluation else "n/a",
            run_result.evaluation.scores.overall_score if run_result.evaluation else "n/a",
            report_path,
        )
    )
    return 0


def _cmd_run_all(args) -> int:
    loaded_scenarios = load_scenarios_from_directory(args.scenario_dir)
    storage = SQLiteStorage(Path(args.db))

    completed = 0
    try:
        for loaded in loaded_scenarios:
            run_id = "cli-{}-{}".format(loaded.scenario.id.lower(), uuid4().hex[:6])
            runner = AgentRunner(
                adapter=DeterministicCliAdapter(),
                tool_registry=create_default_tool_registry(),
                max_steps=args.max_steps,
            )
            run_result = runner.run(loaded, run_id=run_id)
            storage.persist_full_run(loaded, run_result)
            report_path = MarkdownReportGenerator().generate(
                run_result,
                loaded,
                Path(args.report_dir),
            )
            print(
                "run_id={} scenario={} status={} verdict={} report={}".format(
                    run_result.run_id,
                    run_result.scenario_id,
                    run_result.status.value,
                    run_result.evaluation.verdict.value if run_result.evaluation else "n/a",
                    report_path,
                )
            )
            completed += 1
    finally:
        storage.close()

    print("completed_runs={}".format(completed))
    return 0


def _cmd_report(args) -> int:
    storage = SQLiteStorage(Path(args.db))
    try:
        report_path = storage.regenerate_report(args.run_id, Path(args.output_dir))
    finally:
        storage.close()

    print("report={}".format(report_path))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
