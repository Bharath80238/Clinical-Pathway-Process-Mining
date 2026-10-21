"""Process Mining Event Log Validation Module
Author: Amit Prajapati (Member 3 - Process Mining Analyst)
Project: CareFlow: Clinical Pathway Process Mining
"""

from pathlib import Path
import sqlite3
import pandas as pd
import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = PROJECT_ROOT / "data" / "processed" / "careflow.db"
REPORTS_DIR = PROJECT_ROOT / "reports"

def load_raw_analysis_events():
    """Load events from SQLite database for process-specific validation."""
    if not DB_PATH.exists():
        raise FileNotFoundError(f"Database not found at {DB_PATH}")
    with sqlite3.connect(DB_PATH) as conn:
        df = pd.read_sql_query(
            """
            SELECT case_id, activity, event_time, org_group, leucocytes, crp, lactic_acid
            FROM events_analysis
            ORDER BY case_id, event_time ASC
            """,
            conn,
        )
    df["event_time"] = pd.to_datetime(df["event_time"], utc=True)
    return df

def validate_event_log_health(df):
    """Run comprehensive diagnostic checks on event log structure for process mining."""
    total_events = len(df)
    total_cases = df["case_id"].nunique()

    # 1. Null checks
    null_cases = df["case_id"].isna().sum()
    null_activities = df["activity"].isna().sum()
    null_timestamps = df["event_time"].isna().sum()

    # 2. Trace length inspection
    events_per_case = df.groupby("case_id").size()
    single_event_cases = (events_per_case == 1).sum()

    # 3. Timestamp ordering verification
    df["prev_time"] = df.groupby("case_id")["event_time"].shift(1)
    negative_intervals = (df["event_time"] < df["prev_time"]).sum()

    # 4. Same-second simultaneous events
    simultaneous_events = (df["event_time"] == df["prev_time"]).sum()

    # 5. Entry and exit compliance
    first_events = df.groupby("case_id").first()["activity"]
    last_events = df.groupby("case_id").last()["activity"]

    starts_with_reg = (first_events == "ER Registration").sum()
    ends_with_release = last_events.str.startswith("Release").sum()
    ends_with_return = (last_events == "Return ER").sum()

    report = {
        "total_records": int(total_events),
        "total_cases": int(total_cases),
        "null_case_ids": int(null_cases),
        "null_activities": int(null_activities),
        "null_timestamps": int(null_timestamps),
        "single_event_cases": int(single_event_cases),
        "chronological_inversions": int(negative_intervals),
        "simultaneous_events": int(simultaneous_events),
        "cases_starting_er_reg": int(starts_with_reg),
        "cases_starting_er_reg_pct": round((starts_with_reg / total_cases) * 100, 2),
        "cases_ending_release": int(ends_with_release),
        "cases_ending_release_pct": round((ends_with_release / total_cases) * 100, 2),
        "cases_ending_return_er": int(ends_with_return),
        "cases_ending_return_er_pct": round((ends_with_return / total_cases) * 100, 2),
    }

    return report

def main():
    print("Executing Process Mining Event Log Validation...")
    df = load_raw_analysis_events()
    report = validate_event_log_health(df)

    print("\n--- Event Log Health Audit ---")
    for key, value in report.items():
        print(f"  {key}: {value}")

if __name__ == "__main__":
    main()
