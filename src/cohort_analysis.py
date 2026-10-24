"""CareFlow Clinical Cohort Segmentation & Pathway Divergence Analysis
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

def load_cohort_events(db_path=DB_PATH):
    """Load events with clinical attributes for cohort analysis."""
    if not Path(db_path).exists():
        raise FileNotFoundError(f"Database not found at: {db_path}")

    with sqlite3.connect(db_path) as conn:
        df = pd.read_sql_query(
            """
            SELECT case_id, activity, event_time, org_group, age,
                   infection_suspected, sirs_criteria_2_or_more, disfunc_org
            FROM events_analysis
            ORDER BY case_id, event_time ASC
            """,
            conn,
        )

    df["event_time"] = pd.to_datetime(df["event_time"], utc=True)
    return df

def segment_patient_cohorts(df):
    """Identify cohort memberships per patient case."""
    case_meta = df.groupby("case_id").agg(
        start_time=("event_time", "min"),
        end_time=("event_time", "max"),
        event_count=("activity", "count"),
        age=("age", "first"),
        infection_suspected=("infection_suspected", "first"),
        sirs_high_risk=("sirs_criteria_2_or_more", "first"),
        organ_dysfunction=("disfunc_org", "first"),
        activities=("activity", lambda x: set(x)),
    ).reset_index()

    case_meta["duration_days"] = (
        (case_meta["end_time"] - case_meta["start_time"]).dt.total_seconds() / 86400.0
    ).round(2)

    case_meta["has_antibiotics"] = case_meta["activities"].apply(lambda acts: "IV Antibiotics" in acts)
    case_meta["has_icu"] = case_meta["activities"].apply(lambda acts: "Admission IC" in acts)
    case_meta["has_return_er"] = case_meta["activities"].apply(lambda acts: "Return ER" in acts)
    case_meta["is_geriatric"] = case_meta["age"] >= 65

    return case_meta

def compute_cohort_metrics(case_meta):
    """Compute comparative process metrics across clinical cohorts."""
    cohort_definitions = [
        ("All Patients", pd.Series(True, index=case_meta.index)),
        ("Infection Suspected", case_meta["infection_suspected"] == 1),
        ("Infection Not Suspected", case_meta["infection_suspected"] != 1),
        ("ICU Admitted", case_meta["has_icu"]),
        ("Normal Ward Only", ~case_meta["has_icu"]),
        ("High SIRS Risk (>=2)", case_meta["sirs_high_risk"] == 1),
        ("Low SIRS Risk", case_meta["sirs_high_risk"] != 1),
        ("Geriatric (Age >= 65)", case_meta["is_geriatric"]),
        ("Non-Geriatric (Age < 65)", ~case_meta["is_geriatric"]),
    ]

    metrics = []
    total_cohort_cases = len(case_meta)

    for name, mask in cohort_definitions:
        sub = case_meta[mask]
        if sub.empty:
            continue
        
        metrics.append({
            "cohort_name": name,
            "patient_cases": len(sub),
            "share_of_total_pct": round((len(sub) / total_cohort_cases) * 100, 2),
            "median_event_count": int(sub["event_count"].median()),
            "mean_event_count": round(float(sub["event_count"].mean()), 2),
            "median_duration_days": round(float(sub["duration_days"].median()), 2),
            "mean_duration_days": round(float(sub["duration_days"].mean()), 2),
            "antibiotic_admin_rate_pct": round((sub["has_antibiotics"].sum() / len(sub)) * 100, 2),
            "readmission_rate_pct": round((sub["has_return_er"].sum() / len(sub)) * 100, 2),
            "icu_admission_rate_pct": round((sub["has_icu"].sum() / len(sub)) * 100, 2),
        })

    metrics_df = pd.DataFrame(metrics)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    out_csv = REPORTS_DIR / "cohort_comparison_metrics.csv"
    metrics_df.to_csv(out_csv, index=False)
    print(f"Exported cohort metrics table: {out_csv}")
    return metrics_df

def compare_icu_vs_ward_pathways(df, case_meta):
    """Compare transition latencies and Golden Hour antibiotic SLA for ICU vs Ward patients."""
    icu_case_ids = set(case_meta[case_meta["has_icu"]]["case_id"])
    
    df_sorted = df.copy()
    df_sorted["is_icu"] = df_sorted["case_id"].isin(icu_case_ids)
    df_sorted["next_activity"] = df_sorted.groupby("case_id")["activity"].shift(-1)
    df_sorted["next_time"] = df_sorted.groupby("case_id")["event_time"].shift(-1)

    trans = df_sorted.dropna(subset=["next_activity", "next_time"]).copy()
    trans["duration_minutes"] = (
        (trans["next_time"] - trans["event_time"]).dt.total_seconds() / 60.0
    )
    trans = trans[trans["duration_minutes"] >= 0]

    # Sepsis Triage to IV Antibiotics SLA
    sla_trans = trans[
        (trans["activity"].isin(["ER Registration", "ER Triage", "ER Sepsis Triage"]))
        & (trans["next_activity"] == "IV Antibiotics")
    ]

    icu_sla = sla_trans[sla_trans["is_icu"]]["duration_minutes"]
    ward_sla = sla_trans[~sla_trans["is_icu"]]["duration_minutes"]

    comparison = {
        "icu_cohort": {
            "cases": int(len(icu_case_ids)),
            "antibiotic_sla_median_minutes": round(float(icu_sla.median()), 2) if not icu_sla.empty else None,
            "antibiotic_sla_p90_minutes": round(float(np.percentile(icu_sla, 90)), 2) if not icu_sla.empty else None,
            "golden_hour_compliance_pct": round(float((icu_sla <= 60).mean() * 100), 2) if not icu_sla.empty else None,
            "three_hour_bundle_compliance_pct": round(float((icu_sla <= 180).mean() * 100), 2) if not icu_sla.empty else None,
        },
        "ward_cohort": {
            "cases": int(len(case_meta) - len(icu_case_ids)),
            "antibiotic_sla_median_minutes": round(float(ward_sla.median()), 2) if not ward_sla.empty else None,
            "antibiotic_sla_p90_minutes": round(float(np.percentile(ward_sla, 90)), 2) if not ward_sla.empty else None,
            "golden_hour_compliance_pct": round(float((ward_sla <= 60).mean() * 100), 2) if not ward_sla.empty else None,
            "three_hour_bundle_compliance_pct": round(float((ward_sla <= 180).mean() * 100), 2) if not ward_sla.empty else None,
        },
    }

    import json
    comp_path = REPORTS_DIR / "icu_vs_ward_comparison.json"
    with open(comp_path, "w", encoding="utf-8") as f:
        json.dump(comparison, f, indent=2)
    print(f"Exported ICU vs Ward comparison: {comp_path}")
    return comparison

def plot_cohort_metrics(metrics_df):
    """Plot comparative metrics across clinical patient cohorts."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    # Filter specific core cohorts for cleaner presentation
    focus_cohorts = [
        "Infection Suspected", "Infection Not Suspected",
        "ICU Admitted", "Normal Ward Only",
        "Geriatric (Age >= 65)", "Non-Geriatric (Age < 65)",
    ]
    sub = metrics_df[metrics_df["cohort_name"].isin(focus_cohorts)].copy()

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))

    # Subplot 1: Median Length of Stay (Days)
    colors = ["#2980b9", "#7f8c8d", "#c0392b", "#27ae60", "#d35400", "#16a085"]
    bars1 = ax1.barh(sub["cohort_name"], sub["median_duration_days"], color=colors, edgecolor="black", alpha=0.85)
    ax1.set_title("Median Length of Stay by Clinical Cohort (Days)", fontsize=11, fontweight="bold")
    ax1.set_xlabel("Median Duration (Days)", fontsize=10, fontweight="bold")
    for bar in bars1:
        w = bar.get_width()
        ax1.annotate(f"{w:.1f}d", xy=(w, bar.get_y() + bar.get_height() / 2), xytext=(5, 0),
                     textcoords="offset points", ha="left", va="center", fontsize=9, fontweight="bold")

    # Subplot 2: Readmission Rate vs Antibiotic Administration
    y = np.arange(len(sub))
    height = 0.35
    bars_abx = ax2.barh(y - height/2, sub["antibiotic_admin_rate_pct"], height, label="Antibiotic Admin %", color="#3498db", edgecolor="black")
    bars_ret = ax2.barh(y + height/2, sub["readmission_rate_pct"], height, label="Readmission (Return ER) %", color="#e74c3c", edgecolor="black")

    ax2.set_yticks(y)
    ax2.set_yticklabels(sub["cohort_name"], fontsize=9)
    ax2.set_title("Clinical Intervention & Readmission Rate by Cohort", fontsize=11, fontweight="bold")
    ax2.set_xlabel("Percentage (%)", fontsize=10, fontweight="bold")
    ax2.legend(frameon=True, facecolor="white")

    plt.tight_layout()
    chart_path = OUTPUT_DIR / "cohort_comparison_barchart.png"
    plt.savefig(chart_path, dpi=200)
    plt.close()
    print(f"Created cohort comparison chart: {chart_path}")

def plot_icu_sla_comparison(comparison):
    """Plot Golden Hour and 3-hour bundle antibiotic compliance for ICU vs Ward."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    labels = ["ICU Admitted", "Normal Ward Only"]
    golden_hour = [comparison["icu_cohort"]["golden_hour_compliance_pct"], comparison["ward_cohort"]["golden_hour_compliance_pct"]]
    three_hour = [comparison["icu_cohort"]["three_hour_bundle_compliance_pct"], comparison["ward_cohort"]["three_hour_bundle_compliance_pct"]]

    x = np.arange(len(labels))
    width = 0.35

    fig, ax = plt.subplots(figsize=(8, 5))
    bars1 = ax.bar(x - width/2, golden_hour, width, label="Golden Hour Target (<= 60 min)", color="#27ae60", edgecolor="black")
    bars2 = ax.bar(x + width/2, three_hour, width, label="Surviving Sepsis Mandate (<= 180 min)", color="#2980b9", edgecolor="black")

    ax.set_ylabel("Compliance Rate (%)", fontsize=10, fontweight="bold")
    ax.set_title("Antibiotic Administration SLA Compliance: ICU vs Ward", fontsize=11, fontweight="bold")
    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=10, fontweight="bold")
    ax.set_ylim(0, 115)
    ax.legend(frameon=True, facecolor="white")

    for bars in [bars1, bars2]:
        for bar in bars:
            h = bar.get_height()
            ax.annotate(f"{h:.1f}%", xy=(bar.get_x() + bar.get_width() / 2, h), xytext=(0, 3),
                        textcoords="offset points", ha="center", va="bottom", fontsize=9, fontweight="bold")

    plt.tight_layout()
    chart_path = OUTPUT_DIR / "cohort_sepsis_sla_comparison.png"
    plt.savefig(chart_path, dpi=200)
    plt.close()
    print(f"Created SLA comparison chart: {chart_path}")

def main():
    print("Loading events for cohort analysis...")
    df = load_cohort_events()
    print("Segmenting clinical patient cohorts...")
    case_meta = segment_patient_cohorts(df)
    metrics_df = compute_cohort_metrics(case_meta)
    
    print("\nComparing ICU vs Normal Ward pathways...")
    icu_comp = compare_icu_vs_ward_pathways(df, case_meta)

    print("\nGenerating comparative cohort visualizations...")
    plot_cohort_metrics(metrics_df)
    plot_icu_sla_comparison(icu_comp)
    print("\nCohort analysis completed successfully.")

if __name__ == "__main__":
    main()
