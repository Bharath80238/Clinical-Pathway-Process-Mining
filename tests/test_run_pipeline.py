import csv
import sqlite3
import subprocess

import pytest

from src import run_pipeline


def test_verify_database_accepts_valid_database(
    tmp_path, monkeypatch
):
    database = tmp_path / "careflow.db"

    with sqlite3.connect(database) as connection:
        connection.execute(
            "CREATE TABLE events_raw (id INTEGER)"
        )
        connection.execute(
            "INSERT INTO events_raw VALUES (1)"
        )
        connection.execute(
            """
            CREATE TABLE events_analysis (
                case_id TEXT,
                activity TEXT,
                event_time TIMESTAMP,
                org_group TEXT,
                leucocytes REAL,
                crp REAL,
                lactic_acid REAL
            )
            """
        )
        connection.execute(
            """
            INSERT INTO events_analysis
            VALUES ('C1', 'Admission', '2024-01-01', NULL, NULL, NULL, NULL)
            """
        )

    monkeypatch.setattr(run_pipeline, "DATABASE_PATH", database)

    run_pipeline.verify_database(None)


def test_verify_database_rejects_missing_table(
    tmp_path, monkeypatch
):
    database = tmp_path / "careflow.db"

    with sqlite3.connect(database) as connection:
        connection.execute(
            "CREATE TABLE events_raw (id INTEGER)"
        )
        connection.execute(
            "INSERT INTO events_raw VALUES (1)"
        )

    monkeypatch.setattr(run_pipeline, "DATABASE_PATH", database)

    with pytest.raises(RuntimeError, match="missing tables"):
        run_pipeline.verify_database(None)


def test_verify_csv_accepts_valid_report(tmp_path):
    report = tmp_path / "report.csv"

    with report.open("w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["from_activity", "to_activity", "transition_count"])
        writer.writerow(["Admission", "Triage", "10"])

    run_pipeline.verify_csv(
        report,
        None,
        ["from_activity", "to_activity", "transition_count"],
    )


def test_verify_csv_rejects_wrong_columns(tmp_path):
    report = tmp_path / "report.csv"

    with report.open("w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["wrong", "columns"])
        writer.writerow(["A", "B"])

    with pytest.raises(RuntimeError, match="Unexpected CSV columns"):
        run_pipeline.verify_csv(
            report,
            None,
            ["from_activity", "to_activity", "transition_count"],
        )


def test_verify_csv_rejects_empty_report(tmp_path):
    report = tmp_path / "report.csv"

    with report.open("w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["from_activity", "to_activity", "transition_count"])

    with pytest.raises(RuntimeError, match="no data rows"):
        run_pipeline.verify_csv(
            report,
            None,
            ["from_activity", "to_activity", "transition_count"],
        )


def test_verify_figure_accepts_valid_png(tmp_path):
    figure = tmp_path / "figure.png"
    figure.write_bytes(b"\x89PNG\r\n\x1a\n" + b"test image data")

    run_pipeline.verify_figure(
        figure,
        None,
    )


def test_verify_figure_rejects_invalid_png(tmp_path):
    figure = tmp_path / "figure.png"
    figure.write_bytes(b"not a PNG file")

    with pytest.raises(RuntimeError, match="Invalid PNG"):
        run_pipeline.verify_figure(
            figure,
            None,
        )


def test_run_stage_stops_on_subprocess_failure(monkeypatch):
    def failing_run(*args, **kwargs):
        raise subprocess.CalledProcessError(1, ["python", "failed.py"])

    monkeypatch.setattr(run_pipeline.subprocess, "run", failing_run)

    with pytest.raises(subprocess.CalledProcessError):
        run_pipeline.run_stage(
            "Test failure",
            "src/nonexistent.py",
        )



def test_snapshot_outputs_records_existing_file_metadata(tmp_path):
    output = tmp_path / "report.csv"
    output.write_text("old report", encoding="utf-8")

    snapshot = run_pipeline.snapshot_outputs([output])

    assert snapshot[output] == (
        output.stat().st_mtime_ns,
        output.stat().st_size,
    )


def test_verify_fresh_output_rejects_unchanged_file(tmp_path):
    output = tmp_path / "report.csv"
    output.write_text("old report", encoding="utf-8")

    previous_snapshot = run_pipeline.snapshot_outputs([output])[output]

    with pytest.raises(RuntimeError, match="was not modified"):
        run_pipeline.verify_fresh_output(output, previous_snapshot)


def test_verify_fresh_output_accepts_modified_file(tmp_path):
    output = tmp_path / "report.csv"
    output.write_text("old report", encoding="utf-8")

    previous_snapshot = run_pipeline.snapshot_outputs([output])[output]

    output.write_text("new report with updated data", encoding="utf-8")

    run_pipeline.verify_fresh_output(output, previous_snapshot)
