"""Analyze the most frequent consecutive clinical activity transitions."""
from pathlib import Path
import sqlite3
import pandas as pd
PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATABASE_PATH = PROJECT_ROOT / "data" / "processed" / "careflow.db"
OUTPUT_PATH = PROJECT_ROOT / "reports" / "activity_transitions.csv"

def load_events():
    """Load and validate event data from the analysis table."""
    if not DATABASE_PATH.exists():
        raise FileNotFoundError(
            f"Database not found: {DATABASE_PATH}"
        )
    with sqlite3.connect(DATABASE_PATH) as connection:
        events = pd.read_sql_query(
            """
            SELECT case_id, activity, event_time
            FROM events_analysis
            """,
            connection,
        )
    events["case_id"] = events["case_id"].astype("string").str.strip()
    events["activity"] = events["activity"].astype("string").str.strip()
    events["event_time"] = pd.to_datetime(
        events["event_time"], errors="coerce", utc=True
    )
    valid_mask = (
        events["case_id"].notna()
        & events["case_id"].ne("")
        & events["activity"].notna()
        & events["activity"].ne("")
        & events["event_time"].notna()
    )
    invalid_count = int((~valid_mask).sum())
    events = events.loc[valid_mask].copy()
    print(f"Valid events: {len(events):,}")
    print(f"Excluded invalid events: {invalid_count:,}")
    print(f"Distinct case IDs: {events['case_id'].nunique():,}")
    unknown_id_count = int(events["case_id"].eq("NA").sum())
    print(f"Events with literal 'NA' case ID: {unknown_id_count:,}")

    return events
def count_transitions(events):
    """Count consecutive activity pairs within each case."""
    events = events.sort_values(
        ["case_id", "event_time", "activity"],
        kind="mergesort",
    ).copy()
    events["next_activity"] = (
        events.groupby("case_id", sort=False)["activity"].shift(-1)
    )
    transitions = events.loc[
        events["next_activity"].notna(),
        ["case_id", "activity", "next_activity"],
    ].copy()
    transitions = transitions.rename(
        columns={
            "activity": "from_activity",
            "next_activity": "to_activity",
        }
    )
    summary = (
        transitions.groupby(
            ["from_activity", "to_activity"], sort=False
        )
        .size()
        .reset_index(name="transition_count")
        .sort_values(
            ["transition_count", "from_activity", "to_activity"],
            ascending=[False, True, True],
            kind="mergesort",
        )
        .reset_index(drop=True)
    )
    return summary

def main():
    """Generate and save the frequent-transition report."""
    events = load_events()
    transitions = count_transitions(events)
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    transitions.to_csv(OUTPUT_PATH, index=False)
    print("\nTop 20 consecutive activity transitions:")
    print(transitions.head(20).to_string(index=False))
    print(f"\nUnique transitions found: {len(transitions):,}")
    print(f"Saved transition report to: {OUTPUT_PATH}")

if __name__ == "__main__":
    main()