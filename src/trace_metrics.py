"""Case Duration and Trace Length Process Metrics
Author: Amit Prajapati (Member 3 - Process Mining Analyst)
Project: CareFlow: Clinical Pathway Process Mining
"""

from pathlib import Path
import sqlite3
import json
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = PROJECT_ROOT / "data" / "processed" / "careflow.db"
OUTPUT_DIR = PROJECT_ROOT / "reports" / "figures" / "process_maps"
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

def plot_trace_distributions(case_summary):
    """Plot trace length histogram and event count vs case duration scatter."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))

    # 1. Trace length histogram
    counts = case_summary["event_count"]
    p95 = np.percentile(counts, 95)
    counts_filtered = counts[counts <= p95]

    ax1.hist(counts_filtered, bins=25, color="#3498db", edgecolor="black", alpha=0.85)
    ax1.axvline(counts.median(), color="#e74c3c", linestyle="--", linewidth=2, label=f"Median ({counts.median():.0f} events)")
    ax1.axvline(counts.mean(), color="#f39c12", linestyle="-", linewidth=2, label=f"Mean ({counts.mean():.1f} events)")
    ax1.set_title("Trace Length Distribution (Events per Patient Case)", fontsize=11, fontweight="bold")
    ax1.set_xlabel("Number of Recorded Events (up to 95th percentile)", fontsize=10, fontweight="bold")
    ax1.set_ylabel("Patient Cases", fontsize=10, fontweight="bold")
    ax1.legend(frameon=True, facecolor="white")

    # 2. Scatter plot: Event Count vs Duration (Days)
    colors = {
        "Completed Normal Encounter": "#2ecc71",
        "Readmission Encounter": "#e74c3c",
        "Truncated / Open Encounter": "#95a5a6",
    }

    for cat, group in case_summary.groupby("lifecycle_category"):
        # Clip to 95th percentile duration for visual clarity
        p95_days = np.percentile(case_summary["duration_days"], 95)
        grp_filtered = group[group["duration_days"] <= p95_days]
        ax2.scatter(
            grp_filtered["event_count"],
            grp_filtered["duration_days"],
            label=f"{cat} ({len(group)})",
            color=colors.get(cat, "#34495e"),
            alpha=0.65,
            edgecolors="none",
            s=35,
        )

    ax2.set_title("Patient Case Event Count vs Duration (Days)", fontsize=11, fontweight="bold")
    ax2.set_xlabel("Event Count", fontsize=10, fontweight="bold")
    ax2.set_ylabel("Duration in Days (up to 95th percentile)", fontsize=10, fontweight="bold")
    ax2.legend(frameon=True, facecolor="white")

    plt.tight_layout()
    chart_path = OUTPUT_DIR / "trace_duration_vs_events.png"
    plt.savefig(chart_path, dpi=200)
    plt.close()
    print(f"Created trace distribution figure: {chart_path}")

def main():
    print("Loading events...")
    df = load_events()
    case_summary, stats = compute_trace_metrics(df)
    plot_trace_distributions(case_summary)

    print("\n--- Trace Length Distribution (Events per Case) ---")
    for k, v in stats["trace_length"].items():
        print(f"  {k}: {v}")

    print("\n--- Case Duration Distribution (Days) ---")
    for k, v in stats["duration_days"].items():
        print(f"  {k}: {v}")

if __name__ == "__main__":
    main()
