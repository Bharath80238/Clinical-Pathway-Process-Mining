"""CareFlow Clinical Rework & Readmission Loop Analysis Module
Author: Amit Prajapati (Member 3 - Process Mining Analyst)
Project: CareFlow: Clinical Pathway Process Mining
"""

from pathlib import Path
import sqlite3
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

def analyze_rework_and_loops(df):
    """Detect repeated activities, diagnostic rework loops, and readmission cycles."""
    # Count activity occurrences per patient case
    case_act_counts = df.groupby(["case_id", "activity"]).size().reset_index(name="repetition_count")
    rework = case_act_counts[case_act_counts["repetition_count"] > 1].copy()

    # Aggregate by activity
    rework_summary = rework.groupby("activity").agg(
        affected_cases=("case_id", "nunique"),
        total_repetition_events=("repetition_count", "sum"),
        max_repeats_in_single_case=("repetition_count", "max"),
        mean_repeats_when_repeated=("repetition_count", "mean"),
    ).reset_index().sort_values("affected_cases", ascending=False)

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    rework_summary.to_csv(REPORTS_DIR / "rework_analysis.csv", index=False)
    print(f"Exported rework analysis: {REPORTS_DIR / 'rework_analysis.csv'}")

    # Analyze Return ER readmissions
    return_cases = df[df["activity"] == "Return ER"]["case_id"].unique()
    total_cases = df["case_id"].nunique()
    readmission_rate = (len(return_cases) / total_cases) * 100.0

    print(f"Total Patient Cases: {total_cases}")
    print(f"Patients with 'Return ER' Readmissions: {len(return_cases)} ({readmission_rate:.2f}%)")

    return rework_summary, readmission_rate

def plot_rework_frequency(rework_summary):
    """Plot bar chart of most repeated clinical actions."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    plt.figure(figsize=(10, 6))

    sorted_df = rework_summary.sort_values("affected_cases", ascending=True)
    bars = plt.barh(sorted_df["activity"], sorted_df["affected_cases"], color="#e67e22", edgecolor="black", alpha=0.85)

    plt.title("Clinical Activity Rework & Repetition Frequency Across Patients", fontsize=12, fontweight="bold")
    plt.xlabel("Number of Affected Patient Cases (with >= 2 occurrences)", fontsize=10, fontweight="bold")
    plt.ylabel("Clinical Activity", fontsize=10, fontweight="bold")

    for bar in bars:
        w = bar.get_width()
        plt.annotate(
            f"{int(w)} cases",
            xy=(w, bar.get_y() + bar.get_height() / 2),
            xytext=(5, 0),
            textcoords="offset points",
            ha="left",
            va="center",
            fontsize=9,
            fontweight="bold",
        )

    plt.tight_layout()
    out_plot = OUTPUT_DIR / "rework_frequency.png"
    plt.savefig(out_plot, dpi=200)
    plt.close()
    print(f"Saved rework chart: {out_plot}")

def main():
    print("Loading events for rework analysis...")
    df = load_events()
    rework_summary, readmission_rate = analyze_rework_and_loops(df)
    plot_rework_frequency(rework_summary)
    print("Rework analysis completed successfully.")

if __name__ == "__main__":
    main()
