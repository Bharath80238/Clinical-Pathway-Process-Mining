"""CareFlow Organizational Resource Mining & Departmental Analysis
Author: Amit Prajapati (Member 3 - Process Mining Analyst)
Project: CareFlow: Clinical Pathway Process Mining
"""

from pathlib import Path
import sqlite3
import pandas as pd
import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = PROJECT_ROOT / "data" / "processed" / "careflow.db"
OUTPUT_DIR = PROJECT_ROOT / "reports" / "figures" / "process_maps"
REPORTS_DIR = PROJECT_ROOT / "reports"

# Functional mapping of organizational groups to clinical hospital departments
DEPARTMENT_MAPPING = {
    "A": "Emergency Clinical Staff (Team A)",
    "B": "Central Diagnostic Laboratory",
    "C": "Emergency Triage Assessment Unit",
    "E": "Discharge & Outpatient Administration",
    "?": "Emergency Readmission (Unplanned)",
    "L": "Emergency Clinical Staff (Team B)",
    "P": "Intensive Care Unit (ICU Team P)",
    "W": "Intensive Care Unit (ICU Team W)",
    "J": "Intensive Care Unit (ICU Team J)",
    "K": "Intensive Care Unit (ICU Team K)",
}

def get_department_label(code):
    """Resolve org:group code into a standardized clinical department name."""
    if pd.isna(code) or str(code).strip() == "":
        return "Unassigned / Unknown"
    code = str(code).strip()
    if code in DEPARTMENT_MAPPING:
        return DEPARTMENT_MAPPING[code]
    # Wards (F, G, H, I, M, N, O, Q, R, S, T, U, V, X, Y)
    return f"General Inpatient Ward ({code})"

def load_org_events(db_path=DB_PATH):
    """Load events joined with clinical departmental metadata."""
    if not Path(db_path).exists():
        raise FileNotFoundError(f"Database not found at: {db_path}")

    with sqlite3.connect(db_path) as conn:
        df = pd.read_sql_query(
            """
            SELECT case_id, activity, event_time, org_group
            FROM events_analysis
            ORDER BY case_id, event_time ASC
            """,
            conn,
        )

    df["event_time"] = pd.to_datetime(df["event_time"], utc=True)
    df["org_group"] = df["org_group"].fillna("Unassigned").astype(str).str.strip()
    df["department"] = df["org_group"].apply(get_department_label)
    return df

def main():
    print("Loading organizational events...")
    df = load_org_events()
    print(f"Loaded {len(df)} events with {df['org_group'].nunique()} organizational groups.")
    top_orgs = df["department"].value_counts().head(8)
    print("\nTop Organizational Units by Event Volume:")
    for dept, count in top_orgs.items():
        pct = (count / len(df)) * 100
        print(f"  {dept}: {count:,} events ({pct:.2f}%)")

if __name__ == "__main__":
    main()
