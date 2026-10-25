import sqlite3
from pathlib import Path
import pandas as pd
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = PROJECT_ROOT / "data" / "processed" / "careflow.db"
OUTPUT_DIR = PROJECT_ROOT / "reports"
OUTPUT_FILE = OUTPUT_DIR / "common_pathways.csv"
def load_events():
    """Load valid pathway events from the analysis table."""
    if not DB_PATH.exists():
        raise FileNotFoundError(f"Database not found: {DB_PATH}")
    with sqlite3.connect(DB_PATH) as connection:
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
        events["event_time"],
        errors="coerce",
        utc=True,
    )
    valid = (
        events["case_id"].notna()
        & events["case_id"].ne("")
        & events["activity"].notna()
        & events["activity"].ne("")
        & events["event_time"].notna()
    )
    excluded = int((~valid).sum())
    events = events.loc[valid].copy()
    # Keep the literal "NA" identifier, but report it as uncertain.
    events = events.sort_values(
        ["case_id", "event_time", "activity"],
        kind="stable",
    )
    print(f"Valid events: {len(events):,}")
    print(f"Excluded invalid events: {excluded:,}")
    print(f"Distinct case IDs: {events['case_id'].nunique():,}")
    print(
        "Events with literal 'NA' case ID:",
        int(events["case_id"].eq("NA").sum()),
    )
    return events

def find_common_pathways(events, top_n=20):
    """Count distinct ordered activity sequences for each case."""
    case_paths = (
        events.groupby("case_id", sort=True)["activity"]
        .agg(lambda activities: tuple(str(a) for a in activities))
        .tolist()
    )
    pathway_counts = {}
    for pathway in case_paths:
        pathway = tuple(pathway)
        pathway_counts[pathway] = pathway_counts.get(pathway, 0) + 1
    most_common = sorted(
        pathway_counts.items(),
        key=lambda item: (-item[1], item[0]),
    )[:top_n]
    results = [
        {
            "activity_sequence": " -> ".join(pathway),
            "sequence_length": len(pathway),
            "case_count": count,
        }
        for pathway, count in most_common
    ]
    return pd.DataFrame(
        results,
        columns=["activity_sequence", "sequence_length", "case_count"],
    )
def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    events = load_events()
    if events.empty:
        print("No valid events found. No pathway report generated.")
        return
    pathways = find_common_pathways(events)
    if pathways.empty:
        print("No pathways found.")
        return
    pathways.to_csv(OUTPUT_FILE, index=False)
    print("\nMost common complete pathways:")
    print(pathways.to_string(index=False))
    print(f"\nSaved pathway report to: {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
