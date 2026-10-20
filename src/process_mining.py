"""CareFlow Clinical Pathway Process Mining Module
Author: Amit Prajapati (Member 3 - Process Mining Analyst)
Project: CareFlow: Clinical Pathway Process Mining
"""

from pathlib import Path
import sqlite3
import pandas as pd
import pm4py

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = PROJECT_ROOT / "data" / "processed" / "careflow.db"
OUTPUT_DIR = PROJECT_ROOT / "reports" / "figures" / "process_maps"

def load_process_event_log(db_path=DB_PATH):
    """Load and format event data for process mining analysis with PM4Py."""
    if not Path(db_path).exists():
        raise FileNotFoundError(f"Database not found at: {db_path}")

    with sqlite3.connect(db_path) as conn:
        df = pd.read_sql_query(
            """
            SELECT case_id, activity, event_time, org_group, leucocytes, crp, lactic_acid
            FROM events_analysis
            ORDER BY case_id, event_time ASC
            """,
            conn,
        )

    df["event_time"] = pd.to_datetime(df["event_time"], utc=True)

    # Format into PM4Py compliant DataFrame
    event_log = pm4py.format_dataframe(
        df,
        case_id="case_id",
        activity_key="activity",
        timestamp_key="event_time",
    )
    return event_log

def get_process_summary(event_log):
    """Compute foundational process mining metrics."""
    cases = pm4py.get_event_attribute_values(event_log, "case:concept:name")
    activities = pm4py.get_event_attribute_values(event_log, "concept:name")
    start_activities = pm4py.get_start_activities(event_log)
    end_activities = pm4py.get_end_activities(event_log)
    variants = pm4py.get_variants(event_log)

    summary = {
        "total_cases": len(cases),
        "total_events": len(event_log),
        "unique_activities": len(activities),
        "unique_variants": len(variants),
        "start_activities": start_activities,
        "end_activities": end_activities,
    }
    return summary

if __name__ == "__main__":
    log = load_process_event_log()
    summary = get_process_summary(log)
    print("=== Process Mining Summary ===")
    print(f"Total Cases: {summary['total_cases']}")
    print(f"Total Events: {summary['total_events']}")
    print(f"Unique Activities: {summary['unique_activities']}")
    print(f"Unique Pathway Variants: {summary['unique_variants']}")
    print(f"Start Activities: {summary['start_activities']}")
    print(f"End Activities: {summary['end_activities']}")
