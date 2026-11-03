import sqlite3
import pandas as pd
import pytest
from src import pathway_analysis
from src.pathway_analysis import find_common_pathways

def create_sample_events():
    """Create a controlled dataset for pathway testing."""
    return pd.DataFrame({
        "case_id": [
            "CASE_001", "CASE_001", "CASE_001",
            "CASE_002", "CASE_002", "CASE_002",
            "CASE_003", "CASE_003",
        ],
        "activity": [
            "A", "B", "C",
            "A", "B", "C",
            "A", "C",
        ],
    })

@pytest.mark.parametrize("invalid_top_n", [0, -1, 2.5, "5", True])
def test_invalid_top_n_raises_value_error(invalid_top_n):
    events = create_sample_events()
    with pytest.raises(ValueError):
        find_common_pathways(events, top_n=invalid_top_n)

def test_common_pathway_frequency():
    result = find_common_pathways(create_sample_events())
    most_common = result.iloc[0]
    assert most_common["activity_sequence"] == "A -> B -> C"
    assert most_common["case_count"] == 2

def test_sequence_length():
    result = find_common_pathways(create_sample_events())
    assert result.iloc[0]["sequence_length"] == 3

def test_pathway_counts_are_correct():
    result = find_common_pathways(create_sample_events())
    pathway_counts = dict(
        zip(result["activity_sequence"], result["case_count"])
    )
    assert pathway_counts["A -> B -> C"] == 2
    assert pathway_counts["A -> C"] == 1

def test_empty_events():
    events = pd.DataFrame(columns=["case_id", "activity"])
    result = find_common_pathways(events)
    assert result.empty
    assert list(result.columns) == [
        "activity_sequence",
        "sequence_length",
        "case_count",
    ]

def test_repeated_activities_are_preserved():
    events = pd.DataFrame({
        "case_id": ["CASE_001", "CASE_001", "CASE_001"],
        "activity": ["A", "B", "A"],
    })
    result = find_common_pathways(events)
    assert result.iloc[0]["activity_sequence"] == "A -> B -> A"
    assert result.iloc[0]["sequence_length"] == 3

def test_top_n_limits_results():
    result = find_common_pathways(create_sample_events(), top_n=1)
    assert len(result) == 1

def test_load_events_reads_and_sorts_data(tmp_path, monkeypatch):
    db_path = tmp_path / "test_careflow.db"
    with sqlite3.connect(db_path) as connection:
        connection.execute("""
            CREATE TABLE events_analysis (
                case_id TEXT,
                activity TEXT,
                event_time TIMESTAMP
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
    monkeypatch.setattr(pathway_analysis, "DB_PATH", db_path)
    events = pathway_analysis.load_events()
    assert len(events) == 3
    assert events["case_id"].tolist() == [
        "CASE_001", "CASE_001", "CASE_002"
    ]
    case_001 = events[events["case_id"] == "CASE_001"]
    assert case_001["activity"].tolist() == ["A", "B"]

def test_load_events_excludes_invalid_records(tmp_path, monkeypatch):
    db_path = tmp_path / "test_invalid_events.db"
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
    monkeypatch.setattr(pathway_analysis, "DB_PATH", db_path)
    events = pathway_analysis.load_events()
    assert len(events) == 1
    assert events.iloc[0]["case_id"] == "CASE_001"
    assert events.iloc[0]["activity"] == "Admission"

def test_load_events_raises_error_when_database_missing(
    tmp_path, monkeypatch
):
    missing_db = tmp_path / "missing.db"
    monkeypatch.setattr(pathway_analysis, "DB_PATH", missing_db)
    with pytest.raises(FileNotFoundError, match="Database not found"):
        pathway_analysis.load_events()