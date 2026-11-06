
"""Run the complete CareFlow data analysis pipeline."""

import csv
import sqlite3
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATABASE_PATH = PROJECT_ROOT / "data" / "processed" / "careflow.db"

EXPECTED_REPORTS = [
    PROJECT_ROOT / "reports" / "common_pathways.csv",
    PROJECT_ROOT / "reports" / "activity_transitions.csv",
]

EXPECTED_FIGURES = [
    PROJECT_ROOT / "reports" / "figures" / "activity_frequency.png",
    PROJECT_ROOT / "reports" / "figures" / "case_event_counts.png",
    PROJECT_ROOT / "reports" / "figures" / "case_duration_distribution.png",
    PROJECT_ROOT / "reports" / "figures" / "event_interval_distribution.png",
    PROJECT_ROOT / "reports" / "figures" / "repeated_activities.png",
]


def snapshot_outputs(paths):
    """Capture the existing metadata of expected output files."""
    snapshots = {}

    for path in paths:
        if path.is_file():
            stat = path.stat()
            snapshots[path] = (stat.st_mtime_ns, stat.st_size)
        else:
            snapshots[path] = None

    return snapshots


def verify_fresh_output(path, previous_snapshot):
    """Ensure an output file was created or modified during its stage."""
    if not path.is_file():
        raise FileNotFoundError(
            f"Expected output was not generated: {path}"
        )

    stat = path.stat()
    current_snapshot = (stat.st_mtime_ns, stat.st_size)

    if current_snapshot == previous_snapshot:
        raise RuntimeError(
            f"Output was not modified during this run: {path}"
        )


def run_stage(name, script, *arguments):
    """Execute one pipeline stage and stop if it fails."""
    print(f"\n{'=' * 65}")
    print(f"STAGE: {name}")
    print("=" * 65)

    command = [
        sys.executable,
        str(PROJECT_ROOT / script),
        *arguments,
    ]

    subprocess.run(
        command,
        cwd=PROJECT_ROOT,
        check=True,
    )

    print(f"\nPASSED: {name}")


def verify_database(previous_snapshot):
    """Verify the database output, schema, and populated tables."""
    print("\nVerifying SQLite database...")

    verify_fresh_output(DATABASE_PATH, previous_snapshot)

    expected_columns = {
        "events_analysis": {
            "case_id",
            "activity",
            "event_time",
            "org_group",
            "leucocytes",
            "crp",
            "lactic_acid",
        }
    }

    with sqlite3.connect(DATABASE_PATH) as connection:
        tables = {
            row[0]
            for row in connection.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            )
        }

        required_tables = {"events_raw", "events_analysis"}
        missing = required_tables - tables

        if missing:
            raise RuntimeError(
                f"Database is missing tables: {sorted(missing)}"
            )

        counts = {}

        for table in sorted(required_tables):
            counts[table] = connection.execute(
                f'SELECT COUNT(*) FROM "{table}"'
            ).fetchone()[0]

            if counts[table] == 0:
                raise RuntimeError(
                    f"Database table '{table}' is empty."
                )

        for table, expected in expected_columns.items():
            actual = {
                row[1]
                for row in connection.execute(
                    f'PRAGMA table_info("{table}")'
                )
            }

            missing_columns = expected - actual

            if missing_columns:
                raise RuntimeError(
                    f"{table} is missing columns: "
                    f"{sorted(missing_columns)}"
                )

    print("Database verification passed.")

    for table, count in counts.items():
        print(f"{table}: {count:,} rows")


def verify_csv(path, previous_snapshot, expected_columns):
    """Verify CSV freshness, schema, and data rows."""
    verify_fresh_output(path, previous_snapshot)

    with path.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as file:
        reader = csv.DictReader(file)

        if reader.fieldnames != expected_columns:
            raise RuntimeError(
                f"Unexpected CSV columns in {path.name}. "
                f"Expected {expected_columns}, "
                f"got {reader.fieldnames}"
            )

        row_count = 0

        for row in reader:
            if None in row or any(
                value is None for value in row.values()
            ):
                raise RuntimeError(
                    f"Malformed CSV row in {path.name}"
                )

            row_count += 1

    if row_count == 0:
        raise RuntimeError(
            f"Report contains no data rows: {path}"
        )

    print(
        f"Verified report: {path.name} "
        f"({row_count} rows)"
    )


def verify_figure(path, previous_snapshot):
    """Verify PNG freshness, file size, and signature."""
    verify_fresh_output(path, previous_snapshot)

    if path.stat().st_size == 0:
        raise RuntimeError(
            f"Figure is empty: {path}"
        )

    with path.open("rb") as file:
        signature = file.read(8)

    expected_signature = b"\x89PNG\r\n\x1a\n"

    if signature != expected_signature:
        raise RuntimeError(
            f"Invalid PNG file: {path}"
        )

    print(f"Verified figure: {path.name}")


def main():
    """Execute and verify every stage of the CareFlow pipeline."""
    try:
        print("CARE FLOW - END-TO-END PIPELINE")
        print(f"Project directory: {PROJECT_ROOT}")

        run_stage(
            "Source data quality validation",
            "src/data_quality.py",
        )

        database_snapshot = snapshot_outputs([DATABASE_PATH])[DATABASE_PATH]

        run_stage(
            "Database preparation",
            "src/prepare_data.py",
        )
        verify_database(database_snapshot)

        run_stage(
            "SQL analysis",
            "src/run_sql.py",
            "sql/analysis_queries.sql",
        )

        run_stage(
            "KPI SQL analysis",
            "src/run_sql.py",
            "sql/kpi_queries.sql",
        )

        pathway_snapshot = snapshot_outputs([EXPECTED_REPORTS[0]])[
            EXPECTED_REPORTS[0]
        ]

        run_stage(
            "Common pathway analysis",
            "src/pathway_analysis.py",
        )
        verify_csv(
            EXPECTED_REPORTS[0],
            pathway_snapshot,
            [
                "activity_sequence",
                "sequence_length",
                "case_count",
            ],
        )

        transition_snapshot = snapshot_outputs([EXPECTED_REPORTS[1]])[
            EXPECTED_REPORTS[1]
        ]

        run_stage(
            "Activity transition analysis",
            "src/activity_transitions.py",
        )
        verify_csv(
            EXPECTED_REPORTS[1],
            transition_snapshot,
            [
                "from_activity",
                "to_activity",
                "transition_count",
            ],
        )

        figure_snapshots = snapshot_outputs(EXPECTED_FIGURES)

        run_stage(
            "Visualization generation",
            "src/visualize_pathways.py",
        )

        for figure in EXPECTED_FIGURES:
            verify_figure(
                figure,
                figure_snapshots[figure],
            )

        print("\n" + "=" * 65)
        print("PIPELINE COMPLETED SUCCESSFULLY")
        print("=" * 65)
        print("Source data: validated")
        print("Database: generated and verified")
        print("SQL analysis: passed")
        print("KPI SQL analysis: passed")
        print("Pathway report: verified")
        print("Activity transition report: verified")
        print(
            f"Visualizations: {len(EXPECTED_FIGURES)} verified"
        )
        print("\nYou can now launch the dashboard using:")
        print("python -m streamlit run app.py")

    except subprocess.CalledProcessError as error:
        print(
            f"\nPIPELINE FAILED: command returned "
            f"exit code {error.returncode}."
        )
        raise SystemExit(error.returncode) from error

    except Exception as error:
        print(f"\nPIPELINE FAILED: {error}")
        raise SystemExit(1) from error

if __name__ == "__main__":
    main()