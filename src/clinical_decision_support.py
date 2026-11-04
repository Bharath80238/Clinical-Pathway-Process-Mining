"""CareFlow Clinical Decision Support System (CDSS) & Automated Triage Engine
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

def load_patient_cohort(db_path=DB_PATH):
    """Load patient event log and extract clinical features per case."""
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

def compute_decision_support_scores(df):
    """Calculate Sepsis Pathway Escalation Score (SPES) and clinical routing recommendations."""
    patient_records = []

    for case_id, group in df.groupby("case_id"):
        acts = set(group["activity"])
        times = group["event_time"].tolist()

        age = float(group["age"].iloc[0]) if pd.notna(group["age"].iloc[0]) else 50.0
        infection = int(group["infection_suspected"].iloc[0]) if pd.notna(group["infection_suspected"].iloc[0]) else 0
        sirs = int(group["sirs_criteria_2_or_more"].iloc[0]) if pd.notna(group["sirs_criteria_2_or_more"].iloc[0]) else 0
        disfunc = int(group["disfunc_org"].iloc[0]) if pd.notna(group["disfunc_org"].iloc[0]) else 0

        has_icu = 1 if "Admission IC" in acts else 0
        has_ward = 1 if "Admission NC" in acts else 0
        has_readmit = 1 if "Return ER" in acts else 0
        has_abx = 1 if "IV Antibiotics" in acts else 0

        stay_days = round((times[-1] - times[0]).total_seconds() / 86400.0, 2)
        total_events = len(group)

        # Repetitive lab orders
        crp_count = int((group["activity"] == "CRP").sum())
        leuco_count = int((group["activity"] == "Leucocytes").sum())
        lactic_count = int((group["activity"] == "LacticAcid").sum())
        repeat_labs = 1 if (crp_count > 1 or leuco_count > 1 or lactic_count > 1) else 0

        # Calculate Sepsis Pathway Escalation Score (SPES: 0 to 10 scale)
        score = 0
        if infection == 1:
            score += 2
        if sirs == 1:
            score += 2
        if disfunc == 1:
            score += 3
        if age >= 65:
            score += 1
        if repeat_labs == 1:
            score += 1
        if has_icu == 1:
            score += 1

        # Determine Risk Tier & Recommended Pathway
        if score <= 2:
            tier = "Low Risk (Outpatient / Observation)"
            action = "Routine ER evaluation; obtain cultures; evaluate for outpatient discharge within 4-6 hours if hemodynamically stable."
            sla_target = "Standard Golden Hour (<= 60 min if abx required)"
            bed_allocation = "ER Observation Unit"
        elif score <= 5:
            tier = "Moderate Risk (Inpatient Acute Care)"
            action = "Administer broad-spectrum IV Antibiotics within 60 min; admit to Inpatient Normal Care Ward; serial CRP/Leucocyte monitoring every 24h."
            sla_target = "Mandatory Golden Hour (<= 60 min)"
            bed_allocation = "Normal Care Ward (Admission NC)"
        else:
            tier = "High / Critical Risk (ICU Escalation Candidate)"
            action = "Immediate stat IV Antibiotics within 30 min; fluid resuscitation; request early ICU consult; pre-emptive telemetry monitoring."
            sla_target = "Accelerated Golden Hour (<= 30 min)"
            bed_allocation = "Intensive Care Unit (Admission IC)"

        patient_records.append({
            "case_id": case_id,
            "age": age,
            "infection_suspected": infection,
            "sirs_criteria": sirs,
            "organ_dysfunction": disfunc,
            "repeat_lab_orders": repeat_labs,
            "spes_score": score,
            "risk_tier": tier,
            "recommended_action": action,
            "sla_target": sla_target,
            "recommended_bed_allocation": bed_allocation,
            "actual_icu_admission": has_icu,
            "actual_ward_admission": has_ward,
            "actual_readmission": has_readmit,
            "total_stay_days": stay_days,
            "event_count": total_events,
        })

    recommendations_df = pd.DataFrame(patient_records)

    # Calculate population-level CDSS distribution
    tier_counts = recommendations_df["risk_tier"].value_counts().to_dict()
    total_cases = len(recommendations_df)

    summary = {
        "cdss_engine_name": "CareFlow Sepsis Pathway Escalation System (SPES)",
        "total_evaluated_patients": total_cases,
        "scoring_scale": "0 to 10 points",
        "risk_tier_distribution": {
            k: {
                "count": int(v),
                "share_pct": round((v / total_cases) * 100.0, 2),
            }
            for k, v in tier_counts.items()
        },
        "high_risk_escalation_cases": int((recommendations_df["spes_score"] >= 6).sum()),
        "high_risk_escalation_pct": round(float((recommendations_df["spes_score"] >= 6).mean() * 100.0), 2),
        "mean_spes_score": round(float(recommendations_df["spes_score"].mean()), 2),
        "median_spes_score": float(recommendations_df["spes_score"].median()),
    }

    return recommendations_df, summary

def plot_decision_support_matrix(rec_df, summary, output_dir=OUTPUT_DIR):
    """Plot CDSS risk score distribution, recommended bed allocation, and stay duration correlation."""
    output_dir.mkdir(parents=True, exist_ok=True)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

    # Panel 1: SPES Score Histogram with Risk Tiers
    scores = rec_df["spes_score"]
    bins = np.arange(-0.5, 11.5, 1)
    n, b, patches = ax1.hist(scores, bins=bins, edgecolor="black", alpha=0.85, rwidth=0.8)

    # Color patches by risk tier
    for patch, val in zip(patches, range(11)):
        if val <= 2:
            patch.set_facecolor("#2ecc71")  # Low Risk (Green)
        elif val <= 5:
            patch.set_facecolor("#f39c12")  # Moderate Risk (Orange)
        else:
            patch.set_facecolor("#e74c3c")  # High/Critical Risk (Red)

    ax1.axvline(summary["mean_spes_score"], color="#2c3e50", linestyle="--", linewidth=2,
                label=f"Mean SPES Score ({summary['mean_spes_score']})")
    ax1.set_title("Sepsis Pathway Escalation Score (SPES) Distribution", fontsize=11, fontweight="bold")
    ax1.set_xlabel("SPES Score (0 to 10 Scale)", fontsize=10, fontweight="bold")
    ax1.set_ylabel("Patient Cases", fontsize=10, fontweight="bold")
    ax1.set_xticks(range(11))
    ax1.grid(axis="y", linestyle="--", alpha=0.5)

    # Custom legend for risk tiers
    custom_lines = [
        plt.Rectangle((0, 0), 1, 1, facecolor="#2ecc71", edgecolor="black", label=f"Low Risk <=2 ({summary['risk_tier_distribution']['Low Risk (Outpatient / Observation)']['count']} pts)"),
        plt.Rectangle((0, 0), 1, 1, facecolor="#f39c12", edgecolor="black", label=f"Moderate Risk 3-5 ({summary['risk_tier_distribution']['Moderate Risk (Inpatient Acute Care)']['count']} pts)"),
        plt.Rectangle((0, 0), 1, 1, facecolor="#e74c3c", edgecolor="black", label=f"High Risk >=6 ({summary['risk_tier_distribution']['High / Critical Risk (ICU Escalation Candidate)']['count']} pts)"),
    ]
    ax1.legend(handles=custom_lines, loc="upper right", frameon=True, facecolor="white", fontsize=8.5)

    # Panel 2: Recommended Bed Allocation vs Readmission Hazard
    tier_labels = ["Low Risk (0-2)\nER Observation", "Moderate Risk (3-5)\nNormal Care Ward", "Critical Risk (6-10)\nICU Escalation"]
    tier_keys = [
        "Low Risk (Outpatient / Observation)",
        "Moderate Risk (Inpatient Acute Care)",
        "High / Critical Risk (ICU Escalation Candidate)",
    ]
    tier_counts = [summary["risk_tier_distribution"][k]["count"] for k in tier_keys]
    tier_readmit = [
        round(float(rec_df[rec_df["risk_tier"] == k]["actual_readmission"].mean() * 100.0), 1)
        for k in tier_keys
    ]

    x = np.arange(len(tier_labels))
    width = 0.35

    bars_vol = ax2.bar(x - width/2, tier_counts, width, label="Patient Volume", color="#3498db", edgecolor="black", alpha=0.85)
    ax2_twin = ax2.twinx()
    bars_haz = ax2_twin.bar(x + width/2, tier_readmit, width, label="Observed Readmission Rate (%)", color="#e74c3c", edgecolor="black", alpha=0.85)

    ax2.set_xticks(x)
    ax2.set_xticklabels(tier_labels, fontsize=9.5, fontweight="bold")
    ax2.set_ylabel("Patient Cases", fontsize=10, fontweight="bold", color="#3498db")
    ax2_twin.set_ylabel("Readmission Rate (%)", fontsize=10, fontweight="bold", color="#e74c3c")
    ax2.set_title("CDSS Triage Allocation & Empirical Readmission Risk", fontsize=11, fontweight="bold")
    ax2.grid(axis="y", linestyle="--", alpha=0.5)

    for bar in bars_vol:
        h = bar.get_height()
        ax2.annotate(f"{int(h)}", xy=(bar.get_x() + bar.get_width() / 2, h), xytext=(0, 2), textcoords="offset points", ha="center", va="bottom", fontsize=8.5, fontweight="bold")
    for bar in bars_haz:
        h = bar.get_height()
        ax2_twin.annotate(f"{h:.1f}%", xy=(bar.get_x() + bar.get_width() / 2, h), xytext=(0, 2), textcoords="offset points", ha="center", va="bottom", fontsize=8.5, fontweight="bold")

    plt.tight_layout()
    chart_path = output_dir / "clinical_decision_support_matrix.png"
    plt.savefig(chart_path, dpi=200)
    plt.close()
    print(f"Exported CDSS decision support matrix chart: {chart_path}")
    return chart_path

def main():
    print("Executing Clinical Decision Support System (CDSS)...")
    df = load_patient_cohort()
    rec_df, summary = compute_decision_support_scores(df)

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    csv_path = REPORTS_DIR / "clinical_decision_recommendations.csv"
    rec_df.to_csv(csv_path, index=False)
    print(f"Exported CDSS recommendations CSV: {csv_path}")

    json_path = REPORTS_DIR / "clinical_decision_rules.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    print(f"Exported CDSS summary JSON: {json_path}")

    plot_decision_support_matrix(rec_df, summary)

    print("\n--- CDSS Population Risk Stratification ---")
    for tier, data in summary["risk_tier_distribution"].items():
        print(f"  {tier}: {data['count']} patients ({data['share_pct']}%)")
    print(f"High-Risk Critical Escalations: {summary['high_risk_escalation_cases']} ({summary['high_risk_escalation_pct']}%)")
    print("CDSS execution completed successfully.")

if __name__ == "__main__":
    main()
