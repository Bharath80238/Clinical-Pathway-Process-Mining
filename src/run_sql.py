from pathlib import Path
import sqlite3
import sys

ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / "data" / "processed" / "careflow.db"
SQL_PATH = ROOT / "sql" / "analysis_queries.sql"

def main():
    if not DB_PATH.exists():
        raise FileNotFoundError(
            "Database not found. Run python src/prepare_data.py first."
        )
    if not SQL_PATH.exists():
        raise FileNotFoundError(
            f"SQL file not found: {SQL_PATH}"
        )
    sql_text = SQL_PATH.read_text(encoding="utf-8")
    statements = [
        statement.strip()
        for statement in sql_text.split(";")
        if statement.strip()
    ]
    if not statements:
        print("No SQL statements found.")
        sys.exit(1)
    failed_queries = []
    with sqlite3.connect(DB_PATH) as conn:
        for number, statement in enumerate(statements, start=1):
            try:
                cursor = conn.execute(statement)
                rows = cursor.fetchall()
                print(f"\n--- Query {number} ---")
                if cursor.description:
                    print([column[0] for column in cursor.description])
                    for row in rows[:15]:
                        print(row)
                    print(f"Rows returned: {len(rows)}")
                else:
                    print("Query executed successfully.")
            except sqlite3.Error as exc:
                failed_queries.append((number, str(exc)))
                print(f"SQL ERROR in query {number}: {exc}")
    if failed_queries:
        print("\nSQL VALIDATION FAILED")
        for number, error in failed_queries:
            print(f"Query {number}: {error}")
        sys.exit(1)
    print(f"\nSUCCESS: All {len(statements)} SQL queries executed.")
if __name__ == "__main__":
    main()
