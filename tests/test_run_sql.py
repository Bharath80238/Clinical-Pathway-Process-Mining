import sqlite3
import pytest
from src import run_sql

@pytest.fixture
def test_environment(tmp_path, monkeypatch):
    """Create an isolated temporary SQLite database for testing."""
    db_path = tmp_path / "test.db"
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            """
            CREATE TABLE sample (
                id INTEGER PRIMARY KEY,
                name TEXT
            )
            """
        )
        conn.execute(
            "INSERT INTO sample (name) VALUES (?)",
            ("CareFlow",),
        )
    sql_dir = tmp_path / "sql"
    sql_dir.mkdir()
    monkeypatch.setattr(run_sql, "ROOT", tmp_path)
    monkeypatch.setattr(run_sql, "DB_PATH", db_path)
    return tmp_path, sql_dir

def test_custom_sql_file_executes(
    test_environment, monkeypatch, capsys
):
    _, sql_dir = test_environment
    sql_file = sql_dir / "test_query.sql"
    sql_file.write_text(
        "SELECT * FROM sample;",
        encoding="utf-8",
    )
    monkeypatch.setattr(
        "sys.argv",
        ["run_sql.py", "sql/test_query.sql"],
    )
    run_sql.main()
    output = capsys.readouterr().out
    assert "SUCCESS: All 1 SQL queries executed." in output
    assert "CareFlow" in output

def test_missing_sql_file(
    test_environment, monkeypatch, capsys
):
    monkeypatch.setattr(
        "sys.argv",
        ["run_sql.py", "sql/not_found.sql"],
    )
    with pytest.raises(SystemExit) as exc:
        run_sql.main()
    assert exc.value.code == 1
    assert "SQL file not found" in capsys.readouterr().out

def test_empty_sql_file(
    test_environment, monkeypatch, capsys
):
    _, sql_dir = test_environment
    sql_file = sql_dir / "empty.sql"
    sql_file.write_text("", encoding="utf-8")
    monkeypatch.setattr(
        "sys.argv",
        ["run_sql.py", "sql/empty.sql"],
    )
    with pytest.raises(SystemExit) as exc:
        run_sql.main()
    assert exc.value.code == 1
    assert "No SQL statements found" in capsys.readouterr().out

def test_invalid_sql_query(
    test_environment, monkeypatch, capsys
):
    _, sql_dir = test_environment
    sql_file = sql_dir / "invalid.sql"
    sql_file.write_text(
        "SELECT * FROM missing_table;",
        encoding="utf-8",
    )
    monkeypatch.setattr(
        "sys.argv",
        ["run_sql.py", "sql/invalid.sql"],
    )
    with pytest.raises(SystemExit) as exc:
        run_sql.main()
    output = capsys.readouterr().out
    assert exc.value.code == 1
    assert "SQL ERROR" in output
    assert "SQL VALIDATION FAILED" in output

def test_too_many_arguments(monkeypatch, capsys):
    monkeypatch.setattr(
        "sys.argv",
        ["run_sql.py", "first.sql", "second.sql"],
    )
    with pytest.raises(SystemExit) as exc:
        run_sql.main()
    assert exc.value.code == 2
    assert "Usage:" in capsys.readouterr().out

def test_missing_database(
    test_environment, monkeypatch, capsys
):
    root, _ = test_environment
    monkeypatch.setattr(
        run_sql,
        "DB_PATH",
        root / "missing.db",
    )
    monkeypatch.setattr(
        "sys.argv",
        ["run_sql.py"],
    )
    with pytest.raises(SystemExit) as exc:
        run_sql.main()
    assert exc.value.code == 1
    assert "Database not found" in capsys.readouterr().out
