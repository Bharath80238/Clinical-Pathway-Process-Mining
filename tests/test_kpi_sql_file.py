import sqlite3
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / "data" / "processed" / "careflow.db"
SQL_PATH = ROOT / "sql" / "kpi_queries.sql"

@pytest.fixture
def kpi_results():
    """Execute all KPI SQL queries and collect their results."""

    if not DB_PATH.exists():
        pytest.fail("CareFlow database not found.")

    if not SQL_PATH.exists():
        pytest.fail("KPI SQL file not found.")

    sql_text = SQL_PATH.read_text(encoding="utf-8")

    statements = [
        statement.strip()
        for statement in sql_text.split(";")
        if statement.strip()
    ]

    results = []

    with sqlite3.connect(DB_PATH) as connection:
        for statement in statements:
            cursor = connection.execute(statement)
            results.append(cursor.fetchall())

    return results


def test_kpi_file_contains_six_queries(kpi_results):
    assert len(kpi_results) == 6


def test_dataset_overview_query(kpi_results):
    result = kpi_results[0][0]

    assert result[0] == 15213
    assert result[1] == 1050
    assert result[2] == 16


def test_case_duration_query(kpi_results):
    result = kpi_results[1][0]

    assert result[0] == 1050
    assert result[1] == pytest.approx(0.03, abs=0.01)
    assert result[2] == pytest.approx(683.26, abs=0.01)
    assert result[3] == pytest.approx(10135.77, abs=0.01)
    assert result[4] == pytest.approx(128.24, abs=0.01)
    assert result[5] == pytest.approx(2225.3, abs=0.01)


def test_inter_event_interval_query(kpi_results):
    result = kpi_results[2][0]

    assert result == (
        14163, 50.66, 10014.25, 5171, 3677,
        2125, 705, 299, 178,
    )


def test_release_to_return_query(kpi_results):
    result = kpi_results[3]

    assert len(result) == 4

    transitions = {row[0]: row[1] for row in result}

    assert transitions["Release A"] == 276
    assert transitions["Release D"] == 10
    assert transitions["Release C"] == 6
    assert transitions["Release E"] == 1


def test_data_quality_query(kpi_results):
    result = dict(kpi_results[4])

    assert result["Missing case IDs"] == 0
    assert result["Missing activities"] == 0
    assert result["Missing timestamps"] == 0
    assert result["Invalid timestamps"] == 0
    assert result["Literal NA case identifiers"] == 24


def test_activity_inventory_query(kpi_results):
    result = kpi_results[5]

    assert len(result) == 16

    activities = {row[0]: row[1] for row in result}

    assert activities["Leucocytes"] == 3382
    assert activities["CRP"] == 3262
    assert activities["LacticAcid"] == 1466
    assert activities["Return ER"] == 294
    assert activities["Release E"] == 6
