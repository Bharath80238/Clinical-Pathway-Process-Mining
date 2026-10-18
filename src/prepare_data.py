from pathlib import Path
import sqlite3
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
PROCESSED = ROOT / "data" / "processed"
DB_PATH = PROCESSED / "careflow.db"
CASE_COL = "case:concept:name"
ACTIVITY_COL = "concept:name"
TIME_COL = "time:timestamp"

def load_events():
    parquet_path = RAW / "events.parquet"
    excel_path = RAW / "events.xlsx"
    if parquet_path.exists():
        return pd.read_parquet(parquet_path)
    if excel_path.exists():
        print(
            "WARNING: Using Excel copy. "
            "Validate it against the source before final analysis."
        )
        return pd.read_excel(
    excel_path,
    keep_default_na=False,
    na_values=[""],
)
    raise FileNotFoundError(
        "Place events.parquet or events.xlsx inside data/raw/"
    )

def main():
    PROCESSED.mkdir(parents=True, exist_ok=True)
    df = load_events()
    required = [CASE_COL, ACTIVITY_COL, TIME_COL]
    missing = set(required) - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {missing}")
    raw_df = df.copy()
    analysis = pd.DataFrame({
        "case_id": df[CASE_COL],
        "activity": df[ACTIVITY_COL],
        "event_time": pd.to_datetime(
            df[TIME_COL], errors="coerce", utc=True
        ),
    })
    for source_col, output_col in [
        ("org:group", "org_group"),
        ("Leucocytes", "leucocytes"),
        ("CRP", "crp"),
        ("LacticAcid", "lactic_acid"),
    ]:
        if source_col in df.columns:
            analysis[output_col] = df[source_col]
    original_rows = len(analysis)
    analysis = analysis.dropna(
        subset=["case_id", "activity", "event_time"]
    ).copy()
    required_rows = len(analysis)
    duplicate_count = int(analysis.duplicated().sum())
    analysis = analysis.drop_duplicates().copy()
    analysis = analysis.sort_values(
        ["case_id", "event_time", "activity"],
        kind="stable",
    ).reset_index(drop=True)
    print("Loaded rows:", len(raw_df))
    print("Rows before analysis filtering:", original_rows)
    print("Rows after required-field filtering:", required_rows)
    print("Exact duplicates removed from analysis:", duplicate_count)
    print("Final analysis rows:", len(analysis))
    print("Cases in analysis:", analysis["case_id"].nunique())
    with sqlite3.connect(DB_PATH) as conn:
        raw_df.to_sql("events_raw", conn, if_exists="replace", index=False)
        analysis.to_sql(
            "events_analysis", conn, if_exists="replace", index=False
        )
    print("Database created at:", DB_PATH)

if __name__ == "__main__":
    main()
