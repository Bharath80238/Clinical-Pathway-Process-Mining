"""CareFlow Clinical Decision Support System (CDSS) & Automated Triage Engine
Author: Amit Prajapati (Member 3 - Process Mining Analyst)
Project: CareFlow: Clinical Pathway Process Mining
"""

from pathlib import Path
import sqlite3
import json
import pandas as pd
import numpy as np

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

    print("\n--- CDSS Population Risk Stratification ---")
    for tier, data in summary["risk_tier_distribution"].items():
        print(f"  {tier}: {data['count']} patients ({data['share_pct']}%)")
    print(f"High-Risk Critical Escalations: {summary['high_risk_escalation_cases']} ({summary['high_risk_escalation_pct']}%)")
    print("CDSS execution completed successfully.")

if __name__ == "__main__":
    main()
