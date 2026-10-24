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
    """Load raw event log from Parquet, CSV, or Excel format."""
    parquet_path = RAW / "events.parquet"
    csv_path = RAW / "events.csv"
    excel_path = RAW / "events.xlsx"

    if parquet_path.exists():
        print(f"Loading raw events from Parquet: {parquet_path}")
        return pd.read_parquet(parquet_path)
    if csv_path.exists():
        print(f"Loading raw events from CSV: {csv_path}")
        return pd.read_csv(csv_path)
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
        "Place events.parquet, events.csv, or events.xlsx inside data/raw/"
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

    # Optional clinical & organizational attributes
    attribute_mappings = [
        ("org:group", "org_group"),
        ("Leucocytes", "leucocytes"),
        ("CRP", "crp"),
        ("LacticAcid", "lactic_acid"),
        ("Age", "age"),
        ("InfectionSuspected", "infection_suspected"),
        ("DiagnosticBlood", "diagnostic_blood"),
        ("DisfuncOrg", "disfunc_org"),
        ("SIRSCriteria2OrMore", "sirs_criteria_2_or_more"),
        ("DiagnosticArtAstrup", "diagnostic_art_astrup"),
        ("DiagnosticXthorax", "diagnostic_xthorax"),
        ("DiagnosticECG", "diagnostic_ecg"),
        ("Hypoxie", "hypoxie"),
        ("Hypotensie", "hypotensie"),
        ("Oligurie", "oligurie"),
    ]

    for source_col, output_col in attribute_mappings:
        if source_col in df.columns:
            analysis[output_col] = df[source_col]

    # Forward-fill case-level static clinical attributes across all events of each patient
    case_level_cols = [
        "age",
        "infection_suspected",
        "sirs_criteria_2_or_more",
        "disfunc_org",
        "hypoxie",
        "hypotensie",
        "oligurie",
    ]
    for col in case_level_cols:
        if col in analysis.columns:
            analysis[col] = analysis.groupby("case_id")[col].ffill().bfill()

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
