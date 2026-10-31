from pathlib import Path
import sqlite3
import sys

ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / "data" / "processed" / "careflow.db"

def main():
    if len(sys.argv) > 2:
        print("Usage: python src/run_sql.py [sql_file]")
        sys.exit(2)

    if len(sys.argv) == 2:
        sql_path = Path(sys.argv[1])
        if not sql_path.is_absolute():
            sql_path = ROOT / sql_path
    else:
        sql_path = ROOT / "sql" / "analysis_queries.sql"
    if not DB_PATH.exists():
        print(
            "Database not found. "
            "Run python src/prepare_data.py first."
        )
        sys.exit(1)
    if not sql_path.is_file():
        print(f"SQL file not found: {sql_path}")
        sys.exit(1)
    sql_text = sql_path.read_text(encoding="utf-8")
    statements = [
        statement.strip()
        for statement in sql_text.split(";")
        if statement.strip()
    ]
    if not statements:
        print("No SQL statements found.")
        sys.exit(1)
    print(f"Database: {DB_PATH}")
    print(f"SQL file: {sql_path.relative_to(ROOT) if sql_path.is_relative_to(ROOT) else sql_path}")
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