from __future__ import annotations

from pathlib import Path

from act0r.cli import main



def test_cli_list_scenarios(capsys) -> None:
    exit_code = main(["list-scenarios", "--scenario-dir", "scenarios/mvp"])
    captured = capsys.readouterr()

    assert exit_code == 0
    assert "SCN-001" in captured.out
    assert "SCN-006" in captured.out



def test_cli_run_command_persists_and_reports(tmp_path: Path, capsys) -> None:
    db_path = tmp_path / "act0r.sqlite"
    report_dir = tmp_path / "reports"

    exit_code = main(
        [
            "run",
            "--scenario",
            "scenarios/mvp/SCN-001_benign_email_summary.yaml",
            "--db",
            str(db_path),
            "--report-dir",
            str(report_dir),
            "--run-id",
            "cli-test-run",
        ]
    )
    captured = capsys.readouterr()

    assert exit_code == 0
    assert "run_id=cli-test-run" in captured.out
    assert db_path.exists()
    assert (report_dir / "cli-test-run.md").exists()



def test_cli_report_regeneration(tmp_path: Path, capsys) -> None:
    db_path = tmp_path / "act0r.sqlite"
    report_dir = tmp_path / "reports"

    run_exit = main(
        [
            "run",
            "--scenario",
            "scenarios/mvp/SCN-001_benign_email_summary.yaml",
            "--db",
            str(db_path),
            "--report-dir",
            str(report_dir),
            "--run-id",
            "cli-report-run",
        ]
    )
    assert run_exit == 0

    report_path = report_dir / "cli-report-run.md"
    report_path.unlink()

    regen_exit = main(
        [
            "report",
            "--run-id",
            "cli-report-run",
            "--db",
            str(db_path),
            "--output-dir",
            str(report_dir),
        ]
    )
    captured = capsys.readouterr()

    assert regen_exit == 0
    assert "report=" in captured.out
    assert report_path.exists()



def test_cli_run_all(tmp_path: Path, capsys) -> None:
    db_path = tmp_path / "act0r.sqlite"
    report_dir = tmp_path / "reports"

    exit_code = main(
        [
            "run-all",
            "--scenario-dir",
            "scenarios/mvp",
            "--db",
            str(db_path),
            "--report-dir",
            str(report_dir),
            "--max-steps",
            "2",
        ]
    )
    captured = capsys.readouterr()

    assert exit_code == 0
    assert "completed_runs=6" in captured.out
