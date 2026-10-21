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

CLINICAL_ACTIVITY_ORDER = {
    "ER Registration": 1,
    "ER Triage": 2,
    "ER Sepsis Triage": 3,
    "CRP": 4,
    "Leucocytes": 5,
    "LacticAcid": 6,
    "IV Liquid": 7,
    "IV Antibiotics": 8,
    "Admission NC": 9,
    "Admission IC": 10,
    "Release A": 11,
    "Release B": 12,
    "Release C": 13,
    "Release D": 14,
    "Release E": 15,
    "Return ER": 16,
}

def resolve_simultaneous_events(df):
    """Apply clinical precedence rules to resolve same-second simultaneous events deterministically."""
    df_sorted = df.copy()
    df_sorted["clinical_priority"] = df_sorted["activity"].map(CLINICAL_ACTIVITY_ORDER).fillna(99)

    # Sort stably by case_id, timestamp, then clinical priority
    df_sorted = df_sorted.sort_values(
        by=["case_id", "event_time", "clinical_priority"],
        kind="stable",
    ).reset_index(drop=True)

    # Assign intra-second sequence offset to guarantee unique temporal ordering
    df_sorted["intra_second_seq"] = df_sorted.groupby(["case_id", "event_time"]).cumcount()
    df_sorted["resolved_event_time"] = df_sorted["event_time"] + pd.to_timedelta(
        df_sorted["intra_second_seq"], unit="ms"
    )

    print(f"Resolved {len(df_sorted)} events with clinical precedence tie-breaking.")
    return df_sorted

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

def categorize_case_completeness(df):
    """Categorize every patient case into clinical lifecycle outcome states."""
    grouped = df.groupby("case_id")
    case_outcomes = []

    for case_id, group in grouped:
        acts = group["activity"].tolist()
        has_release = any(a.startswith("Release") for a in acts)
        has_return = "Return ER" in acts
        last_act = acts[-1] if acts else "None"

        if has_return:
            category = "Readmission Encounter"
        elif has_release:
            category = "Completed Normal Encounter"
        else:
            category = "Truncated / Open Encounter"

        case_outcomes.append({
            "case_id": case_id,
            "lifecycle_status": category,
            "last_recorded_activity": last_act,
            "has_release": has_release,
            "has_return_er": has_return,
            "trace_length": len(acts),
        })

    outcomes_df = pd.DataFrame(case_outcomes)
    summary = outcomes_df["lifecycle_status"].value_counts().to_dict()

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    summary_out = REPORTS_DIR / "case_completeness_summary.json"
    import json
    with open(summary_out, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    print(f"Exported case completeness summary: {summary_out}")
    return outcomes_df, summary

def main():
    print("Executing Process Mining Event Log Validation...")
    df = load_raw_analysis_events()
    report = validate_event_log_health(df)

    print("\n--- Event Log Health Audit ---")
    for key, value in report.items():
        print(f"  {key}: {value}")

    print("\n--- Case Lifecycle Completeness Breakdown ---")
    outcomes_df, summary = categorize_case_completeness(df)
    for cat, count in summary.items():
        pct = (count / len(outcomes_df)) * 100
        print(f"  {cat}: {count} cases ({pct:.2f}%)")

    print("\n--- Resolving Simultaneous Same-Second Events ---")
    df_resolved = resolve_simultaneous_events(df)
    simul_after = (df_resolved["resolved_event_time"] == df_resolved.groupby("case_id")["resolved_event_time"].shift(1)).sum()
    print(f"  Simultaneous timestamps after resolution: {simul_after}")

if __name__ == "__main__":
    main()
