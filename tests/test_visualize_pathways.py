
import sqlite3

import pandas as pd
import pytest

from src import visualize_pathways


def create_sample_events():
    """Create sample events stored in an unsorted order."""
    return pd.DataFrame({
        "case_id": [
            "CASE_001", "CASE_001", "CASE_001",
            "CASE_002", "CASE_002",
        ],
        "activity": ["C", "A", "B", "D", "E"],
        "event_time": pd.to_datetime([
            "2024-01-01 12:00:00",
            "2024-01-01 10:00:00",
            "2024-01-01 11:00:00",
            "2024-01-01 10:00:00",
            "2024-01-01 11:00:00",
        ], utc=True),
    })


def test_calculate_case_durations():
    events = create_sample_events()

    result = visualize_pathways.calculate_case_durations(events)

    assert len(result) == 2
    assert result["CASE_001"] == 2.0
    assert result["CASE_002"] == 1.0


def test_calculate_case_durations_excludes_missing_values():
    events = pd.DataFrame({
        "case_id": ["CASE_001", "CASE_001", None],
        "activity": ["A", "B", "C"],
        "event_time": pd.to_datetime([
            "2024-01-01 10:00:00",
            "2024-01-01 11:00:00",
            "2024-01-01 12:00:00",
        ], utc=True),
    })

    result = visualize_pathways.calculate_case_durations(events)

    assert len(result) == 1
    assert result["CASE_001"] == 1.0


def test_calculate_case_durations_returns_empty_for_invalid_data():
    events = pd.DataFrame({
        "case_id": [None],
        "activity": ["A"],
        "event_time": pd.to_datetime([None], utc=True),
    })

    result = visualize_pathways.calculate_case_durations(events)

    assert result.empty
    assert result.name == "duration_hours"


def test_calculate_waiting_times_uses_chronological_order():
    events = create_sample_events()

    result = visualize_pathways.calculate_waiting_times(events)

    assert len(result) == 3
    assert result.tolist() == [60.0, 60.0, 60.0]


def test_calculate_waiting_times_does_not_cross_case_boundaries():
    events = create_sample_events()

    result = visualize_pathways.calculate_waiting_times(events)

    assert len(result) == len(events) - 2


def test_calculate_waiting_times_preserves_repeated_activities():
    events = pd.DataFrame({
        "case_id": ["CASE_001", "CASE_001", "CASE_001"],
        "activity": ["A", "A", "B"],
        "event_time": pd.to_datetime([
            "2024-01-01 10:00:00",
            "2024-01-01 11:00:00",
            "2024-01-01 12:00:00",
        ], utc=True),
    })

    result = visualize_pathways.calculate_waiting_times(events)

    assert result.tolist() == [60.0, 60.0]


def test_calculate_waiting_times_returns_empty_for_empty_data():
    events = pd.DataFrame(
        columns=["case_id", "activity", "event_time"]
    )

    result = visualize_pathways.calculate_waiting_times(events)

    assert result.empty


def test_load_events_reads_database(tmp_path, monkeypatch):
    db_path = tmp_path / "test_visualization.db"

    with sqlite3.connect(db_path) as connection:
        connection.execute("""
            CREATE TABLE events_analysis (
                case_id TEXT,
                activity TEXT,
                event_time TEXT
            )
        """)
        connection.executemany(
            """
            INSERT INTO events_analysis
            (case_id, activity, event_time)
            VALUES (?, ?, ?)
            """,
            [
                ("CASE_001", "Admission", "2024-01-01 10:00:00"),
                ("CASE_001", "Triage", "2024-01-01 11:00:00"),
            ],
        )

    monkeypatch.setattr(visualize_pathways, "DB_PATH", db_path)

    events = visualize_pathways.load_events()

    assert len(events) == 2
    assert events["case_id"].nunique() == 1
    assert events["event_time"].notna().all()


def test_load_events_raises_error_when_database_missing(
    tmp_path, monkeypatch
):
    missing_db = tmp_path / "missing.db"

    monkeypatch.setattr(visualize_pathways, "DB_PATH", missing_db)

    with pytest.raises(FileNotFoundError, match="Database not found"):
        visualize_pathways.load_events()


def test_chart_generation_creates_all_five_files(
    tmp_path, monkeypatch
):
    output_dir = tmp_path / "figures"

    monkeypatch.setattr(
        visualize_pathways, "OUTPUT_DIR", output_dir
    )

    output_dir.mkdir(parents=True)

    events = create_sample_events()
    repeated_event = events.iloc[[0]].copy()
    repeated_event["event_time"] = pd.Timestamp(
        "2024-01-01 13:00:00", tz="UTC"
)
    events = pd.concat(
    [events, repeated_event],
    ignore_index=True,
)
    visualize_pathways.save_activity_frequency(events)
    visualize_pathways.save_case_event_counts(events)
    visualize_pathways.save_duration_distribution(events)
    visualize_pathways.save_waiting_time_distribution(events)
    visualize_pathways.save_repeated_activities(events)

    expected_files = [
        "activity_frequency.png",
        "case_event_counts.png",
        "case_duration_distribution.png",
        "event_interval_distribution.png",
        "repeated_activities.png",
    ]

    for filename in expected_files:
        assert (output_dir / filename).is_file()
        assert (output_dir / filename).stat().st_size > 0
