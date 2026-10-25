"""CareFlow Heuristic Process Mining & Dependency Net Module
Author: Amit Prajapati (Member 3 - Process Mining Analyst)
Project: CareFlow: Clinical Pathway Process Mining
"""

from pathlib import Path
import sqlite3
import pandas as pd
import numpy as np
import pm4py

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = PROJECT_ROOT / "data" / "processed" / "careflow.db"
OUTPUT_DIR = PROJECT_ROOT / "reports" / "figures" / "process_maps"
REPORTS_DIR = PROJECT_ROOT / "reports"

def load_process_event_log(db_path=DB_PATH):
    """Load and format event data for heuristic mining with PM4Py."""
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

    event_log = pm4py.format_dataframe(
        df,
        case_id="case_id",
        activity_key="activity",
        timestamp_key="event_time",
    )
    return event_log

def compute_causal_dependency_matrix(event_log):
    """Compute formal heuristic dependency scores between all clinical activity pairs."""
    dfg, start_activities, end_activities = pm4py.discover_dfg(event_log)
    activities = sorted(list(pm4py.get_event_attribute_values(event_log, "concept:name").keys()))

    dep_records = []
    for a in activities:
        for b in activities:
            ab_count = dfg.get((a, b), 0)
            ba_count = dfg.get((b, a), 0)

            if a == b:
                # Self-loop dependency measure
                dep_score = ab_count / (ab_count + 1.0)
            else:
                # Causal dependency measure between distinct activities
                total = ab_count + ba_count
                dep_score = (ab_count - ba_count) / (total + 1.0) if total > 0 else 0.0

            if ab_count > 0:
                dep_records.append({
                    "activity_from": a,
                    "activity_to": b,
                    "frequency_a_to_b": ab_count,
                    "frequency_b_to_a": ba_count,
                    "dependency_score": round(float(dep_score), 4),
                    "is_self_loop": (a == b),
                })

    dep_df = pd.DataFrame(dep_records).sort_values("dependency_score", ascending=False).reset_index(drop=True)
    return dep_df, dfg, start_activities, end_activities

def main():
    print("Loading event log for Heuristic Mining...")
    log = load_process_event_log()
    print(f"Loaded {log['case:concept:name'].nunique()} patient cases, {len(log)} events.")

    print("\nComputing Causal Dependency Matrix...")
    dep_df, dfg, start_acts, end_acts = compute_causal_dependency_matrix(log)

    print("\nTop Strong Causal Dependencies (Dependency Score >= 0.7):")
    strong = dep_df[dep_df["dependency_score"] >= 0.7]
    print(strong[["activity_from", "activity_to", "frequency_a_to_b", "dependency_score"]].head(10).to_string(index=False))

if __name__ == "__main__":
    main()
