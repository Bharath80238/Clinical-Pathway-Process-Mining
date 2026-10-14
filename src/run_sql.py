
from pathlib import Path
import sqlite3
ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / "data" / "processed" / "careflow.db"
SQL_PATH = ROOT / "sql" / "analysis_queries.sql"

def main():
    if not DB_PATH.exists():
        raise FileNotFoundError(
            "Run python src/prepare_data.py first."
        )
    sql_text = SQL_PATH.read_text(encoding="utf-8")
    with sqlite3.connect(DB_PATH) as conn:
        for number, statement in enumerate(sql_text.split(";"), start=1):
            statement = statement.strip()
            if not statement or statement.startswith("--"):
                continue
            try:
                cursor = conn.execute(statement)
                rows = cursor.fetchall()
                print(f"\n--- Query {number} ---")
                if cursor.description:
                    print([col[0] for col in cursor.description])
                    for row in rows[:15]:
                        print(row)
                    print(f"Rows returned: {len(rows)}")
            except sqlite3.Error as exc:
                print(f"SQL error in statement {number}: {exc}")

if __name__ == "__main__":
    main()