"""Case Duration and Trace Length Process Metrics
Author: Amit Prajapati (Member 3 - Process Mining Analyst)
Project: CareFlow: Clinical Pathway Process Mining
"""

from pathlib import Path
import sqlite3
import json
import pandas as pd
import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = PROJECT_ROOT / "data" / "processed" / "careflow.db"
REPORTS_DIR = PROJECT_ROOT / "reports"

def load_events():
    with sqlite3.connect(DB_PATH) as conn:
        df = pd.read_sql_query(
            """
            SELECT case_id, activity, event_time, org_group
            FROM events_analysis
            ORDER BY case_id, event_time ASC
            """,
            conn,
        )
    df["event_time"] = pd.to_datetime(df["event_time"], utc=True)
    return df

def compute_trace_metrics(df):
    """Compute case-level duration, event counts, and variance metrics."""
    case_summary = df.groupby("case_id").agg(
        start_time=("event_time", "min"),
        end_time=("event_time", "max"),
        event_count=("activity", "count"),
        unique_activities=("activity", "nunique"),
        first_activity=("activity", "first"),
        last_activity=("activity", "last"),
    ).reset_index()

    case_summary["duration_seconds"] = (
        case_summary["end_time"] - case_summary["start_time"]
    ).dt.total_seconds()
    case_summary["duration_hours"] = (case_summary["duration_seconds"] / 3600.0).round(2)
    case_summary["duration_days"] = (case_summary["duration_seconds"] / 86400.0).round(2)

    # Add clinical flags per case
    case_acts = df.groupby("case_id")["activity"].apply(set)
    case_summary["has_return_er"] = case_summary["case_id"].map(lambda cid: "Return ER" in case_acts.get(cid, set()))
    case_summary["has_iv_antibiotics"] = case_summary["case_id"].map(lambda cid: "IV Antibiotics" in case_acts.get(cid, set()))
    case_summary["has_admission_ic"] = case_summary["case_id"].map(lambda cid: "Admission IC" in case_acts.get(cid, set()))
    case_summary["has_admission_nc"] = case_summary["case_id"].map(lambda cid: "Admission NC" in case_acts.get(cid, set()))

    # Lifecycle classification
    def classify_lifecycle(row):
        if row["has_return_er"]:
            return "Readmission Encounter"
        elif str(row["last_activity"]).startswith("Release"):
            return "Completed Normal Encounter"
        else:
            return "Truncated / Open Encounter"

    case_summary["lifecycle_category"] = case_summary.apply(classify_lifecycle, axis=1)

    # Export trace-level CSV
    trace_csv_path = REPORTS_DIR / "trace_level_metrics.csv"
    case_summary.to_csv(trace_csv_path, index=False)
    print(f"Exported trace-level metrics: {trace_csv_path}")

    # Overall statistical distributions
    stats = {
        "case_count": int(len(case_summary)),
        "trace_length": {
            "mean": round(float(case_summary["event_count"].mean()), 2),
            "median": int(case_summary["event_count"].median()),
            "std": round(float(case_summary["event_count"].std()), 2),
            "min": int(case_summary["event_count"].min()),
            "p25": int(np.percentile(case_summary["event_count"], 25)),
            "p75": int(np.percentile(case_summary["event_count"], 75)),
            "p90": int(np.percentile(case_summary["event_count"], 90)),
            "p95": int(np.percentile(case_summary["event_count"], 95)),
            "max": int(case_summary["event_count"].max()),
        },
        "duration_days": {
            "mean": round(float(case_summary["duration_days"].mean()), 2),
            "median": round(float(case_summary["duration_days"].median()), 2),
            "std": round(float(case_summary["duration_days"].std()), 2),
            "min": round(float(case_summary["duration_days"].min()), 2),
            "p25": round(float(np.percentile(case_summary["duration_days"], 25)), 2),
            "p75": round(float(np.percentile(case_summary["duration_days"], 75)), 2),
            "p90": round(float(np.percentile(case_summary["duration_days"], 90)), 2),
            "p95": round(float(np.percentile(case_summary["duration_days"], 95)), 2),
            "max": round(float(case_summary["duration_days"].max()), 2),
        },
    }

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    stats_out = REPORTS_DIR / "trace_summary_statistics.json"
    with open(stats_out, "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=2)
    print(f"Exported trace statistics JSON: {stats_out}")

    return case_summary, stats

def main():
    print("Loading events...")
    df = load_events()
    case_summary, stats = compute_trace_metrics(df)

    print("\n--- Trace Length Distribution (Events per Case) ---")
    for k, v in stats["trace_length"].items():
        print(f"  {k}: {v}")

    print("\n--- Case Duration Distribution (Days) ---")
    for k, v in stats["duration_days"].items():
        print(f"  {k}: {v}")

if __name__ == "__main__":
    main()
