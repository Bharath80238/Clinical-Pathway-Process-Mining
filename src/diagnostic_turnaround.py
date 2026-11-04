"""CareFlow Diagnostic Turnaround Time (TAT) and Lab Queueing Analyzer
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
REPORTS_DIR = PROJECT_ROOT / "reports"
OUTPUT_DIR = REPORTS_DIR / "figures" / "process_maps"

def load_data(db_path=DB_PATH):
    """Load events from careflow SQLite database."""
    if not Path(db_path).exists():
        raise FileNotFoundError(f"Database not found at {db_path}")

    with sqlite3.connect(db_path) as conn:
        df = pd.read_sql_query(
            """
            SELECT case_id, activity, event_time, org_group, leucocytes, crp, lactic_acid, age, infection_suspected
            FROM events_analysis
            ORDER BY case_id, event_time ASC
            """,
            conn,
        )

    df["event_time"] = pd.to_datetime(df["event_time"], utc=True)
    return df

def analyze_diagnostic_turnaround(df):
    """Compute per-assay turnaround times and lab queueing statistics."""
    lab_assays = ["CRP", "LacticAcid", "Leucocytes"]
    triage_activities = {"ER Registration", "ER Triage", "ER Sepsis Triage"}

    # Extract first triage time per case
    triage_events = df[df["activity"].isin(triage_activities)]
    triage_first = triage_events.groupby("case_id")["event_time"].min().rename("triage_time")

    # Extract first IV Antibiotics time per case
    abx_events = df[df["activity"] == "IV Antibiotics"]
    abx_first = abx_events.groupby("case_id")["event_time"].min().rename("abx_time")

    assay_stats = []
    case_tat_records = {}

    for assay in lab_assays:
        assay_events = df[df["activity"] == assay].copy()
        
        # Test count per case
        test_counts = assay_events.groupby("case_id").size()
        cases_with_test = len(test_counts)
        cases_with_repeat = int((test_counts > 1).sum())
        repeat_rate_pct = round((cases_with_repeat / cases_with_test) * 100.0, 2) if cases_with_test > 0 else 0.0

        # First occurrence of this assay
        first_test = assay_events.groupby("case_id")["event_time"].min().rename(f"{assay}_first_time")

        # Merge with triage time
        merged = pd.concat([triage_first, first_test, abx_first], axis=1, join="inner")
        
        # Calculate TAT from triage to test in minutes
        merged["tat_minutes"] = (merged[f"{assay}_first_time"] - merged["triage_time"]).dt.total_seconds() / 60.0
        
        # Filter non-negative TATs
        valid_tat = merged[merged["tat_minutes"] >= 0]["tat_minutes"]

        # Calculate time from test to antibiotics
        merged["test_to_abx_minutes"] = (merged["abx_time"] - merged[f"{assay}_first_time"]).dt.total_seconds() / 60.0

        median_tat = round(float(valid_tat.median()), 2)
        mean_tat = round(float(valid_tat.mean()), 2)
        p25_tat = round(float(valid_tat.quantile(0.25)), 2)
        p75_tat = round(float(valid_tat.quantile(0.75)), 2)
        p90_tat = round(float(valid_tat.quantile(0.90)), 2)
        iqr_tat = round(p75_tat - p25_tat, 2)

        # SLA compliance benchmarks
        within_30m = round(float((valid_tat <= 30).mean() * 100.0), 2)
        within_60m = round(float((valid_tat <= 60).mean() * 100.0), 2)
        within_120m = round(float((valid_tat <= 120).mean() * 100.0), 2)

        assay_stats.append({
            "assay": assay,
            "total_tested_cases": cases_with_test,
            "total_test_events": len(assay_events),
            "cases_with_repetition": cases_with_repeat,
            "repetition_rate_pct": repeat_rate_pct,
            "median_tat_minutes": median_tat,
            "mean_tat_minutes": mean_tat,
            "p25_tat_minutes": p25_tat,
            "p75_tat_minutes": p75_tat,
            "p90_tat_minutes": p90_tat,
            "iqr_tat_minutes": iqr_tat,
            "pct_within_30min": within_30m,
            "pct_within_60min": within_60m,
            "pct_within_120min": within_120m,
        })

    metrics_df = pd.DataFrame(assay_stats)

    total_cases = df["case_id"].nunique()
    total_lab_events = len(df[df["activity"].isin(lab_assays)])

    summary = {
        "total_cohort_cases": total_cases,
        "total_laboratory_events": total_lab_events,
        "laboratory_share_of_all_events_pct": round((total_lab_events / len(df)) * 100.0, 2),
        "assays_analyzed": lab_assays,
        "assay_metrics": assay_stats,
    }

    return metrics_df, summary

def plot_diagnostic_turnaround(metrics_df, output_dir=OUTPUT_DIR):
    """Plot multi-panel diagnostic turnaround time comparison and repetition metrics."""
    output_dir.mkdir(parents=True, exist_ok=True)
    fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(18, 5))

    assays = metrics_df["assay"]
    x = np.arange(len(assays))
    width = 0.35

    # Panel 1: Median vs 90th Percentile Turnaround Time
    bars1 = ax1.bar(x - width/2, metrics_df["median_tat_minutes"], width, label="Median TAT", color="#2980b9", edgecolor="black", alpha=0.85)
    bars2 = ax1.bar(x + width/2, metrics_df["p90_tat_minutes"], width, label="90th Percentile TAT", color="#e74c3c", edgecolor="black", alpha=0.85)
    ax1.set_title("Diagnostic Turnaround Time (Minutes)", fontsize=11, fontweight="bold")
    ax1.set_ylabel("Turnaround Time (Minutes)", fontsize=10, fontweight="bold")
    ax1.set_xticks(x)
    ax1.set_xticklabels(assays, fontsize=10, fontweight="bold")
    ax1.axhline(60, color="#f39c12", linestyle="--", linewidth=1.5, label="60-min Golden SLA Target")
    ax1.legend(frameon=True, facecolor="white", fontsize=9)
    ax1.grid(axis="y", linestyle="--", alpha=0.5)

    for bar in bars1:
        h = bar.get_height()
        ax1.annotate(f"{h:.1f}m", xy=(bar.get_x() + bar.get_width() / 2, h), xytext=(0, 2), textcoords="offset points", ha="center", va="bottom", fontsize=8, fontweight="bold")
    for bar in bars2:
        h = bar.get_height()
        ax1.annotate(f"{h:.1f}m", xy=(bar.get_x() + bar.get_width() / 2, h), xytext=(0, 2), textcoords="offset points", ha="center", va="bottom", fontsize=8, fontweight="bold")

    # Panel 2: Repetition / Re-testing Rate
    bars3 = ax2.bar(assays, metrics_df["repetition_rate_pct"], color="#8e44ad", edgecolor="black", alpha=0.85, width=0.5)
    ax2.set_title("Assay Re-testing Rate (% Patients Tested >= 2x)", fontsize=11, fontweight="bold")
    ax2.set_ylabel("Patients with Repeat Tests (%)", fontsize=10, fontweight="bold")
    ax2.set_ylim(0, 100)
    ax2.grid(axis="y", linestyle="--", alpha=0.5)

    for bar in bars3:
        h = bar.get_height()
        ax2.annotate(f"{h:.1f}%", xy=(bar.get_x() + bar.get_width() / 2, h), xytext=(0, 3), textcoords="offset points", ha="center", va="bottom", fontsize=9, fontweight="bold")

    # Panel 3: SLA Adherence Distribution (Within 30m, 60m, 120m)
    w3 = 0.25
    b_30 = ax3.bar(x - w3, metrics_df["pct_within_30min"], w3, label="<= 30 min", color="#27ae60", edgecolor="black", alpha=0.85)
    b_60 = ax3.bar(x, metrics_df["pct_within_60min"], w3, label="<= 60 min", color="#f39c12", edgecolor="black", alpha=0.85)
    b_120 = ax3.bar(x + w3, metrics_df["pct_within_120min"], w3, label="<= 120 min", color="#2c3e50", edgecolor="black", alpha=0.85)
    ax3.set_title("SLA Turnaround Benchmark Compliance (%)", fontsize=11, fontweight="bold")
    ax3.set_ylabel("Compliance Rate (%)", fontsize=10, fontweight="bold")
    ax3.set_xticks(x)
    ax3.set_xticklabels(assays, fontsize=10, fontweight="bold")
    ax3.set_ylim(0, 110)
    ax3.legend(frameon=True, facecolor="white", fontsize=9)
    ax3.grid(axis="y", linestyle="--", alpha=0.5)

    plt.tight_layout()
    chart_path = output_dir / "diagnostic_turnaround_distribution.png"
    plt.savefig(chart_path, dpi=200)
    plt.close()
    print(f"Exported diagnostic turnaround chart: {chart_path}")
    return chart_path

def main():
    print("Loading event log for diagnostic turnaround analysis...")
    df = load_data()
    metrics_df, summary = analyze_diagnostic_turnaround(df)

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    csv_path = REPORTS_DIR / "diagnostic_turnaround_metrics.csv"
    metrics_df.to_csv(csv_path, index=False)
    print(f"Exported diagnostic turnaround CSV: {csv_path}")

    json_path = REPORTS_DIR / "diagnostic_turnaround_summary.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    print(f"Exported diagnostic turnaround summary JSON: {json_path}")

    plot_diagnostic_turnaround(metrics_df)

    print("\n--- Diagnostic Turnaround Metrics ---")
    for stat in summary["assay_metrics"]:
        print(f"Assay: {stat['assay']}")
        print(f"  Tested Cases: {stat['total_tested_cases']} ({stat['total_test_events']} events)")
        print(f"  Repetition Rate: {stat['repetition_rate_pct']}%")
        print(f"  Median TAT: {stat['median_tat_minutes']} min (p90: {stat['p90_tat_minutes']} min)")
        print(f"  Within 60 min: {stat['pct_within_60min']}%")

if __name__ == "__main__":
    main()
