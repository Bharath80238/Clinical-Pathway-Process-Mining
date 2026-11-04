import sqlite3
import pandas as pd
import pytest
from src import activity_transitions

def create_sample_events():
    """Create events deliberately stored in an unsorted order."""
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

def test_transitions_are_counted_in_timestamp_order():
    result = activity_transitions.count_transitions(
        create_sample_events()
    )
    counts = dict(zip(
        zip(result["from_activity"], result["to_activity"]),
        result["transition_count"],
    ))
    assert counts[("A", "B")] == 1
    assert counts[("B", "C")] == 1
    assert counts[("D", "E")] == 1

def test_transitions_do_not_cross_case_boundaries():
    result = activity_transitions.count_transitions(
        create_sample_events()
    )
    pairs = list(zip(
        result["from_activity"],
        result["to_activity"],
    ))
    assert ("C", "D") not in pairs

def test_repeated_activities_are_preserved():
    events = pd.DataFrame({
        "case_id": ["CASE_001", "CASE_001", "CASE_001"],
        "activity": ["A", "A", "B"],
        "event_time": pd.to_datetime([
            "2024-01-01 10:00:00",
            "2024-01-01 11:00:00",
            "2024-01-01 12:00:00",
        ], utc=True),
    })
    result = activity_transitions.count_transitions(events)
    counts = dict(zip(
        zip(result["from_activity"], result["to_activity"]),
        result["transition_count"],
    ))
    assert counts[("A", "A")] == 1
    assert counts[("A", "B")] == 1

def test_same_timestamp_uses_alphabetical_activity_order():
    events = pd.DataFrame({
        "case_id": ["CASE_001", "CASE_001", "CASE_001"],
        "activity": ["B", "A", "C"],
        "event_time": pd.to_datetime([
            "2024-01-01 10:00:00",
            "2024-01-01 10:00:00",
            "2024-01-01 11:00:00",
        ], utc=True),
    })
    result = activity_transitions.count_transitions(events)
    pairs = list(zip(
        result["from_activity"],
        result["to_activity"],
    ))
    assert ("A", "B") in pairs
    assert ("B", "C") in pairs

def test_empty_events_return_empty_transition_report():
    events = pd.DataFrame(
        columns=["case_id", "activity", "event_time"]
    )
    result = activity_transitions.count_transitions(events)
    assert result.empty
    assert list(result.columns) == [
        "from_activity",
        "to_activity",
        "transition_count",
    ]

def test_transition_counts_are_sorted_correctly():
    result = activity_transitions.count_transitions(
        create_sample_events()
    )
    assert result["transition_count"].tolist() == sorted(
        result["transition_count"].tolist(),
        reverse=True,
    )

def test_load_events_reads_and_sorts_data(tmp_path, monkeypatch):
    db_path = tmp_path / "test_transitions.db"
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
                ("CASE_001", "B", "2024-01-02 10:00:00"),
                ("CASE_001", "A", "2024-01-01 10:00:00"),
                ("CASE_002", "C", "2024-01-01 09:00:00"),
            ],
        )
    monkeypatch.setattr(
        activity_transitions, "DATABASE_PATH", db_path
    )
    events = activity_transitions.load_events()
    assert len(events) == 3
    assert set(events["activity"]) == {"A", "B", "C"}

def test_load_events_excludes_invalid_records(tmp_path, monkeypatch):
    db_path = tmp_path / "test_invalid_transitions.db"
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
                (None, "Triage", "2024-01-01 11:00:00"),
                ("CASE_002", None, "2024-01-01 12:00:00"),
                ("CASE_003", "Treatment", "invalid-date"),
                ("", "Triage", "2024-01-01 13:00:00"),
                ("CASE_004", "", "2024-01-01 14:00:00"),
            ],
        )
    monkeypatch.setattr(
        activity_transitions, "DATABASE_PATH", db_path
    )
    events = activity_transitions.load_events()
    assert len(events) == 1
    assert events.iloc[0]["case_id"] == "CASE_001"
    assert events.iloc[0]["activity"] == "Admission"

def test_load_events_raises_error_when_database_missing(
    tmp_path, monkeypatch
):
    missing_db = tmp_path / "missing.db"
    monkeypatch.setattr(
        activity_transitions, "DATABASE_PATH", missing_db
    )
    with pytest.raises(FileNotFoundError, match="Database not found"):
        activity_transitions.load_events()