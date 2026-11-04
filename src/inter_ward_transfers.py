"""CareFlow Inter-Ward Transfer Latency and Patient Flow Analyzer
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
    """Load ordered events log for transfer analysis."""
    if not Path(db_path).exists():
        raise FileNotFoundError(f"Database not found at {db_path}")

    with sqlite3.connect(db_path) as conn:
        df = pd.read_sql_query(
            """
            SELECT case_id, activity, event_time, org_group, age, infection_suspected, sirs_criteria_2_or_more
            FROM events_analysis
            ORDER BY case_id, event_time ASC
            """,
            conn,
        )

    df["event_time"] = pd.to_datetime(df["event_time"], utc=True)
    return df

def analyze_inter_ward_transfers(df):
    """Analyze latency and frequency of patient ward-to-ward transfers."""
    # Compute step transitions
    df_sorted = df.sort_values(by=["case_id", "event_time"]).copy()
    df_sorted["next_activity"] = df_sorted.groupby("case_id")["activity"].shift(-1)
    df_sorted["next_time"] = df_sorted.groupby("case_id")["event_time"].shift(-1)
    df_sorted["next_org"] = df_sorted.groupby("case_id")["org_group"].shift(-1)

    # Calculate transition latency in hours
    df_sorted["duration_hours"] = (df_sorted["next_time"] - df_sorted["event_time"]).dt.total_seconds() / 3600.0

    # Filter valid transitions
    valid_transitions = df_sorted.dropna(subset=["next_activity"]).copy()

    # Identify key clinical transfer pathways
    target_transitions = [
        ("ER Sepsis Triage", "Admission NC", "ER to Normal Care Ward"),
        ("ER Sepsis Triage", "Admission IC", "ER to Intensive Care (Direct)"),
        ("Admission NC", "Admission IC", "ICU Escalation (Ward to ICU)"),
        ("Admission IC", "Admission NC", "ICU Step-Down (ICU to Ward)"),
        ("Admission NC", "Release A", "Ward Discharge (Routine)"),
        ("Admission NC", "Release B", "Ward Discharge (Specialized)"),
        ("Admission IC", "Release A", "Direct ICU Discharge"),
        ("Release A", "Return ER", "Post-Discharge Emergency Readmission"),
        ("Admission NC", "Return ER", "Ward Failure to ER Readmission"),
        ("Admission IC", "Return ER", "ICU Escalation to ER Readmission"),
    ]

    metrics_rows = []
    for src, dst, label in target_transitions:
        sub = valid_transitions[(valid_transitions["activity"] == src) & (valid_transitions["next_activity"] == dst)]
        count = len(sub)
        if count > 0:
            durations = sub["duration_hours"]
            metrics_rows.append({
                "source_activity": src,
                "target_activity": dst,
                "transfer_label": label,
                "transition_count": int(count),
                "median_duration_hours": round(float(durations.median()), 2),
                "mean_duration_hours": round(float(durations.mean()), 2),
                "p25_duration_hours": round(float(durations.quantile(0.25)), 2),
                "p75_duration_hours": round(float(durations.quantile(0.75)), 2),
                "p90_duration_hours": round(float(durations.quantile(0.90)), 2),
                "max_duration_hours": round(float(durations.max()), 2),
            })
        else:
            metrics_rows.append({
                "source_activity": src,
                "target_activity": dst,
                "transfer_label": label,
                "transition_count": 0,
                "median_duration_hours": 0.0,
                "mean_duration_hours": 0.0,
                "p25_duration_hours": 0.0,
                "p75_duration_hours": 0.0,
                "p90_duration_hours": 0.0,
                "max_duration_hours": 0.0,
            })

    metrics_df = pd.DataFrame(metrics_rows)

    # Calculate case-level transfer summaries
    patient_cases = df.groupby("case_id").agg(
        has_er_triage=("activity", lambda x: "ER Sepsis Triage" in set(x)),
        has_ward_admission=("activity", lambda x: "Admission NC" in set(x)),
        has_icu_admission=("activity", lambda x: "Admission IC" in set(x)),
        has_readmission=("activity", lambda x: "Return ER" in set(x)),
        age=("age", "first"),
        infection_suspected=("infection_suspected", "first"),
    )

    total_patients = len(patient_cases)
    ward_patients = int(patient_cases["has_ward_admission"].sum())
    icu_patients = int(patient_cases["has_icu_admission"].sum())
    readmission_patients = int(patient_cases["has_readmission"].sum())

    # Direct ICU vs Ward Escalation
    icu_cases = set(df[df["activity"] == "Admission IC"]["case_id"].unique())
    ward_cases = set(df[df["activity"] == "Admission NC"]["case_id"].unique())
    both_cases = icu_cases.intersection(ward_cases)

    summary = {
        "total_evaluated_cases": total_patients,
        "ward_admission_cases": ward_patients,
        "ward_admission_pct": round((ward_patients / total_patients) * 100.0, 2),
        "icu_admission_cases": icu_patients,
        "icu_admission_pct": round((icu_patients / total_patients) * 100.0, 2),
        "multi_ward_transfer_cases": len(both_cases),
        "multi_ward_transfer_pct": round((len(both_cases) / total_patients) * 100.0, 2),
        "total_readmission_cases": readmission_patients,
        "readmission_rate_pct": round((readmission_patients / total_patients) * 100.0, 2),
        "key_transitions": metrics_rows,
    }

    return metrics_df, summary

def plot_inter_ward_delays(metrics_df, output_dir=OUTPUT_DIR):
    """Plot inter-ward transfer latency comparison and transition volumes."""
    output_dir.mkdir(parents=True, exist_ok=True)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))

    # Filter transitions with > 0 occurrences
    active = metrics_df[metrics_df["transition_count"] > 0].sort_values(by="median_duration_hours", ascending=True)

    labels = active["transfer_label"]
    y_pos = np.arange(len(labels))

    # Panel 1: Median Latency in Hours
    bars1 = ax1.barh(y_pos, active["median_duration_hours"], color="#3498db", edgecolor="black", alpha=0.85)
    ax1.set_yticks(y_pos)
    ax1.set_yticklabels(labels, fontsize=9)
    ax1.set_xlabel("Median Duration (Hours)", fontsize=10, fontweight="bold")
    ax1.set_title("Inter-Ward Patient Transfer Latency (Median Hours)", fontsize=11, fontweight="bold")
    ax1.grid(axis="x", linestyle="--", alpha=0.5)

    for bar in bars1:
        w = bar.get_width()
        ax1.annotate(
            f"{w:.1f}h",
            xy=(w, bar.get_y() + bar.get_height() / 2),
            xytext=(4, 0),
            textcoords="offset points",
            va="center",
            fontsize=9,
            fontweight="bold",
        )

    # Panel 2: Transition Volumes
    bars2 = ax2.barh(y_pos, active["transition_count"], color="#e67e22", edgecolor="black", alpha=0.85)
    ax2.set_yticks(y_pos)
    ax2.set_yticklabels([""] * len(labels))
    ax2.set_xlabel("Transition Count (Patients)", fontsize=10, fontweight="bold")
    ax2.set_title("Inter-Ward Transfer Pathway Frequency", fontsize=11, fontweight="bold")
    ax2.grid(axis="x", linestyle="--", alpha=0.5)

    for bar in bars2:
        w = bar.get_width()
        ax2.annotate(
            f"{int(w):,}",
            xy=(w, bar.get_y() + bar.get_height() / 2),
            xytext=(4, 0),
            textcoords="offset points",
            va="center",
            fontsize=9,
            fontweight="bold",
        )

    plt.tight_layout()
    chart_path = output_dir / "inter_ward_transfer_delays.png"
    plt.savefig(chart_path, dpi=200)
    plt.close()
    print(f"Exported inter-ward transfer chart: {chart_path}")
    return chart_path

def main():
    print("Loading event log for inter-ward transfer analysis...")
    df = load_data()
    metrics_df, summary = analyze_inter_ward_transfers(df)

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    csv_path = REPORTS_DIR / "inter_ward_transfer_metrics.csv"
    metrics_df.to_csv(csv_path, index=False)
    print(f"Exported transfer metrics CSV: {csv_path}")

    json_path = REPORTS_DIR / "inter_ward_transfers_summary.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    print(f"Exported transfer summary JSON: {json_path}")

    plot_inter_ward_delays(metrics_df)

    print("\n--- Key Inter-Ward Transfer Metrics ---")
    print(f"Total Evaluated Patients: {summary['total_evaluated_cases']}")
    print(f"Ward Admission Cases: {summary['ward_admission_cases']} ({summary['ward_admission_pct']}%)")
    print(f"ICU Admission Cases: {summary['icu_admission_cases']} ({summary['icu_admission_pct']}%)")
    print(f"Multi-Ward Transfers: {summary['multi_ward_transfer_cases']} ({summary['multi_ward_transfer_pct']}%)")
    print(f"Total Readmissions (Return ER): {summary['total_readmission_cases']} ({summary['readmission_rate_pct']}%)")

if __name__ == "__main__":
    main()
