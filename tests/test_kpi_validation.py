import sqlite3
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / "data" / "processed" / "careflow.db"
@pytest.fixture
def db_connection():
    """Connect to the actual CareFlow analysis database."""
    if not DB_PATH.exists():
        pytest.fail(
            "CareFlow database not found. "
            "Run python src/prepare_data.py first."
        )
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    yield connection
    connection.close()

def test_total_events(db_connection):
    result = db_connection.execute(
        "SELECT COUNT(*) FROM events_analysis"
    ).fetchone()[0]
    assert result == 15213

def test_total_cases(db_connection):
    result = db_connection.execute(
        "SELECT COUNT(DISTINCT case_id) FROM events_analysis"
    ).fetchone()[0]
    assert result == 1050

def test_total_activities(db_connection):
    result = db_connection.execute(
        "SELECT COUNT(DISTINCT activity) FROM events_analysis"
    ).fetchone()[0]
    assert result == 16

def test_total_consecutive_intervals(db_connection):
    result = db_connection.execute(
        """
        WITH ordered_events AS (
            SELECT
                case_id,
                LEAD(event_time) OVER (
                    PARTITION BY case_id
                    ORDER BY event_time, activity
                ) AS next_event_time
            FROM events_analysis
        )
        SELECT COUNT(*)
        FROM ordered_events
        WHERE next_event_time IS NOT NULL
        """
    ).fetchone()[0]
    assert result == 14163

def test_intervals_over_one_hour(db_connection):
    result = db_connection.execute(
        """
        WITH ordered_events AS (
            SELECT
                case_id,
                event_time,
                LEAD(event_time) OVER (
                    PARTITION BY case_id
                    ORDER BY event_time, activity
                ) AS next_event_time
            FROM events_analysis
        ),
        intervals AS (
            SELECT
                unixepoch(next_event_time) -
                unixepoch(event_time) AS interval_seconds
            FROM ordered_events
            WHERE next_event_time IS NOT NULL
        )
        SELECT COUNT(*)
        FROM intervals
        WHERE interval_seconds > 3600
        """
    ).fetchone()[0]
    assert result == 5171

@pytest.mark.parametrize(
    "column",
    ["case_id", "activity", "event_time"],
)
def test_required_columns_have_no_missing_values(
    db_connection, column
):
    result = db_connection.execute(
        f"SELECT COUNT(*) FROM events_analysis "
        f"WHERE {column} IS NULL"
    ).fetchone()[0]
    assert result == 0
