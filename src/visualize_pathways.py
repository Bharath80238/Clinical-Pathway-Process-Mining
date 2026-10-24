import sqlite3
from pathlib import Path
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = PROJECT_ROOT / "data" / "processed" / "careflow.db"
OUTPUT_DIR = PROJECT_ROOT / "reports" / "figures"

def load_events():
    """Load and validate the event data from SQLite."""
    if not DB_PATH.exists():
        raise FileNotFoundError(f"Database not found: {DB_PATH}")

    with sqlite3.connect(DB_PATH) as connection:
        tables = pd.read_sql_query(
            "SELECT name FROM sqlite_master WHERE type='table'",
            connection,
        )
        if "events_analysis" not in tables["name"].tolist():
            raise ValueError(
                "Table 'events_analysis' was not found in the database."
            )
        events = pd.read_sql_query(
            """
            SELECT case_id, activity, event_time
            FROM events_analysis
            """,
            connection,
        )
    required = {"case_id", "activity", "event_time"}
    missing = required - set(events.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")
    events["event_time"] = pd.to_datetime(
        events["event_time"], errors="coerce", utc=True
    )
    print(f"Events loaded: {len(events)}")
    print(f"Cases found: {events['case_id'].nunique()}")
    print(f"Invalid or missing timestamps: {events['event_time'].isna().sum()}")
    return events

def save_activity_frequency(events):
    """Plot the 15 most frequent activities."""
    counts = (
        events["activity"]
        .dropna()
        .value_counts()
        .head(15)
        .sort_values()
    )
    if counts.empty:
        print("Skipping activity chart: no activity values.")
        return
    ax = counts.plot(kind="barh", figsize=(10, 6))
    ax.set_title("Top 15 Clinical Activities by Event Count")
    ax.set_xlabel("Number of events")
    ax.set_ylabel("Activity")
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "activity_frequency.png", dpi=150)
    plt.close()
    print("Created activity_frequency.png")

def save_case_event_counts(events):
    """Plot the 15 cases with the most recorded events."""
    counts = (
        events.dropna(subset=["case_id"])
        .groupby("case_id")
        .size()
        .nlargest(15)
        .sort_values()
    )
    if counts.empty:
        print("Skipping case chart: no case IDs.")
        return
    ax = counts.plot(kind="barh", figsize=(10, 6))
    ax.set_title("Top 15 Cases by Recorded Event Count")
    ax.set_xlabel("Number of events")
    ax.set_ylabel("Case ID")
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "case_event_counts.png", dpi=150)
    plt.close()
    print("Created case_event_counts.png")

def calculate_case_durations(events):
    """Calculate elapsed time between each case's first and last event."""
    valid = events.dropna(subset=["case_id", "event_time"])
    if valid.empty:
        return pd.Series(dtype=float, name="duration_hours")
    times = valid.groupby("case_id")["event_time"].agg(["min", "max"])
    durations = (times["max"] - times["min"]).dt.total_seconds() / 3600
    return durations.rename("duration_hours")

def save_duration_distribution(events):
    """Plot the distribution of elapsed case durations."""
    durations = calculate_case_durations(events).dropna()
    durations = durations[durations >= 0]
    if durations.empty:
        print("Skipping duration chart: no valid durations.")
        return
    plt.figure(figsize=(10, 6))
    plt.hist(durations, bins=20, edgecolor="black")
    plt.title("Distribution of Recorded Case Durations")
    plt.xlabel("Elapsed time (hours)")
    plt.ylabel("Number of cases")
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "case_duration_distribution.png", dpi=150)
    plt.close()
    print("Created case_duration_distribution.png")
    print(f"Median case duration: {durations.median():.2f} hours")

def calculate_waiting_times(events):
    """Calculate elapsed time between consecutive recorded events."""
    valid = events.dropna(subset=["case_id", "activity", "event_time"])
    ordered = valid.sort_values(
        ["case_id", "event_time", "activity"]
    ).copy()
    ordered["next_time"] = (
        ordered.groupby("case_id")["event_time"].shift(-1)
    )
    waiting = (
        ordered["next_time"] - ordered["event_time"]
    ).dt.total_seconds() / 60
    return waiting[waiting >= 0].dropna()

def save_waiting_time_distribution(events):
    """Plot elapsed time between consecutive recorded events."""
    waiting = calculate_waiting_times(events)
    if waiting.empty:
        print("Skipping waiting-time chart: no valid intervals.")
        return
    upper = waiting.quantile(0.95)
    displayed = waiting[waiting <= upper]
    plt.figure(figsize=(10, 6))
    plt.hist(displayed, bins=20, edgecolor="black")
    plt.title("Intervals Between Consecutive Recorded Events")
    plt.xlabel("Elapsed time (minutes; up to 95th percentile)")
    plt.ylabel("Number of intervals")
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "event_interval_distribution.png", dpi=150)
    plt.close()
    print("Created event_interval_distribution.png")
    print(f"Median event interval: {waiting.median():.2f} minutes")
    print(f"95th percentile: {upper:.2f} minutes")
    
def save_repeated_activities(events):
    """Plot the most frequent repeated case-activity combinations."""
    counts = (
        events.dropna(subset=["case_id", "activity"])
        .groupby(["case_id", "activity"])
        .size()
        .rename("occurrences")
        .reset_index()
    )
    repeated = counts[counts["occurrences"] > 1]
    repeated = repeated.nlargest(15, "occurrences")
    if repeated.empty:
        print("Skipping repeated-activity chart: no repeats found.")
        return
    labels = (
        repeated["case_id"].astype(str)
        + " — "
        + repeated["activity"].astype(str)
    )
    chart_data = pd.Series(
        repeated["occurrences"].to_numpy(),
        index=labels,
    ).sort_values()
    ax = chart_data.plot(kind="barh", figsize=(11, 7))
    ax.set_title("Most Frequent Repeated Case-Activity Combinations")
    ax.set_xlabel("Occurrences")
    ax.set_ylabel("Case ID — Activity")
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "repeated_activities.png", dpi=150)
    plt.close()
    print("Created repeated_activities.png")

def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    events = load_events()
    if events.empty:
        print("The events_analysis table is empty. No charts generated.")
        return
    save_activity_frequency(events)
    save_case_event_counts(events)
    save_duration_distribution(events)
    save_waiting_time_distribution(events)
    save_repeated_activities(events)
    print(f"\nVisualization output directory: {OUTPUT_DIR}")
    
if __name__ == "__main__":
    main()
