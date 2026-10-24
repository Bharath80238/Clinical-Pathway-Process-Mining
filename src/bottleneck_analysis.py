"""CareFlow Bottleneck & Transition Duration Analysis Module
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

def load_ordered_events(db_path=DB_PATH):
    """Load chronologically sorted events per case from SQLite."""
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
    return df

def calculate_transition_matrix(df):
    """Calculate transition duration statistics between all consecutive activity pairs."""
    # Lead activity and timestamp within each case
    df["next_activity"] = df.groupby("case_id")["activity"].shift(-1)
    df["next_time"] = df.groupby("case_id")["event_time"].shift(-1)

    transitions = df.dropna(subset=["next_activity", "next_time"]).copy()
    transitions["duration_seconds"] = (
        transitions["next_time"] - transitions["event_time"]
    ).dt.total_seconds()

    # Filter out potential negative artifacts if any
    transitions = transitions[transitions["duration_seconds"] >= 0].copy()
    transitions["duration_hours"] = transitions["duration_seconds"] / 3600.0
    transitions["duration_minutes"] = transitions["duration_seconds"] / 60.0

    grouped = transitions.groupby(["activity", "next_activity"]).agg(
        transition_count=("duration_seconds", "count"),
        mean_hours=("duration_hours", "mean"),
        median_hours=("duration_hours", "median"),
        p75_hours=("duration_hours", lambda x: np.percentile(x, 75)),
        p90_hours=("duration_hours", lambda x: np.percentile(x, 90)),
        p95_hours=("duration_hours", lambda x: np.percentile(x, 95)),
        max_hours=("duration_hours", "max"),
        median_minutes=("duration_minutes", "median"),
    ).reset_index()

    grouped = grouped.sort_values("transition_count", ascending=False).reset_index(drop=True)
    
    # Export CSV
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    out_csv = REPORTS_DIR / "transition_duration_matrix.csv"
    grouped.to_csv(out_csv, index=False)
    print(f"Exported transition duration matrix: {out_csv}")
    return transitions, grouped

def plot_sepsis_antibiotic_sla(transitions):
    """Evaluate and plot the clinical Sepsis 'Golden Hour' SLA: Triage to IV Antibiotics."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    abx = transitions[
        (transitions["activity"].isin(["ER Registration", "ER Triage", "ER Sepsis Triage"]))
        & (transitions["next_activity"] == "IV Antibiotics")
    ].copy()

    if abx.empty:
        print("No direct ER Triage -> IV Antibiotics transition found.")
        return

    median_mins = abx["duration_minutes"].median()
    p90_mins = np.percentile(abx["duration_minutes"], 90)

    plt.figure(figsize=(10, 6))
    displayed = abx["duration_minutes"][abx["duration_minutes"] <= 360]  # First 6 hours
    plt.hist(displayed, bins=25, color="#2b5c8f", edgecolor="black", alpha=0.85)

    # Threshold guidelines: 60 mins (Golden Hour) and 180 mins (Surviving Sepsis 3-hour bundle)
    plt.axvline(60, color="#2ca02c", linestyle="--", linewidth=2, label="Golden Hour Target (60 min)")
    plt.axvline(180, color="#d62728", linestyle="--", linewidth=2, label="Surviving Sepsis Mandate (180 min)")
    plt.axvline(median_mins, color="#ff7f0e", linestyle="-", linewidth=2, label=f"Observed Median ({median_mins:.1f} min)")

    plt.title("ER to IV Antibiotics Time Delay (Sepsis Clinical SLA)", fontsize=12, fontweight="bold")
    plt.xlabel("Delay in Minutes (up to 360 min)", fontsize=10, fontweight="bold")
    plt.ylabel("Number of Patients", fontsize=10, fontweight="bold")
    plt.legend(frameon=True, facecolor="white")
    plt.tight_layout()

    out_plot = OUTPUT_DIR / "sepsis_golden_hour_sla.png"
    plt.savefig(out_plot, dpi=200)
    plt.close()
    print(f"Created sepsis SLA figure: {out_plot}")

def plot_top_bottlenecks(grouped, top_n=12):
    """Plot horizontal bar chart of the highest delay clinical transitions."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    # Filter transitions with at least 50 occurrences to avoid rare outliers dominating
    robust = grouped[grouped["transition_count"] >= 50].copy()
    top_delays = robust.nlargest(top_n, "median_hours").sort_values("median_hours", ascending=True)

    labels = top_delays["activity"] + " -> " + top_delays["next_activity"]

    plt.figure(figsize=(12, 7))
    bars = plt.barh(labels, top_delays["median_hours"], color="#c0392b", alpha=0.85, edgecolor="black")

    plt.title(f"Top {top_n} Clinical Process Bottlenecks by Median Transition Delay", fontsize=12, fontweight="bold")
    plt.xlabel("Median Duration Between Activities (Hours)", fontsize=11, fontweight="bold")
    plt.ylabel("Clinical Step Transition", fontsize=11, fontweight="bold")

    for bar in bars:
        w = bar.get_width()
        plt.annotate(
            f"{w:.1f} hrs",
            xy=(w, bar.get_y() + bar.get_height() / 2),
            xytext=(5, 0),
            textcoords="offset points",
            ha="left",
            va="center",
            fontsize=9,
            fontweight="bold",
        )

    plt.tight_layout()
    out_plot = OUTPUT_DIR / "bottleneck_heatmap.png"
    plt.savefig(out_plot, dpi=200)
    plt.close()
    print(f"Created bottleneck chart: {out_plot}")

def main():
    print("Loading ordered events for bottleneck analysis...")
    df = load_ordered_events()
    print(f"Loaded {len(df)} events across {df['case_id'].nunique()} patient cases.")

    print("\nCalculating inter-activity transition durations...")
    transitions, grouped = calculate_transition_matrix(df)
    
    print("\nEvaluating Sepsis Golden Hour SLA...")
    plot_sepsis_antibiotic_sla(transitions)

    print("\nPlotting top operational bottlenecks...")
    plot_top_bottlenecks(grouped)

    print("\nBottleneck analysis completed successfully.")

if __name__ == "__main__":
    main()
