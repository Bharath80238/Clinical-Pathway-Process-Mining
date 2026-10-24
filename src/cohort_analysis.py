"""CareFlow Clinical Cohort Segmentation & Pathway Divergence Analysis
Author: Amit Prajapati (Member 3 - Process Mining Analyst)
Project: CareFlow: Clinical Pathway Process Mining
"""

from pathlib import Path
import sqlite3
import pandas as pd
import numpy as np

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

def main():
    print("Loading events for cohort analysis...")
    df = load_cohort_events()
    print("Segmenting clinical patient cohorts...")
    case_meta = segment_patient_cohorts(df)
    metrics_df = compute_cohort_metrics(case_meta)
    
    print("\nComparing ICU vs Normal Ward pathways...")
    icu_comp = compare_icu_vs_ward_pathways(df, case_meta)
    print(f"  ICU Golden Hour Compliance (<=60m): {icu_comp['icu_cohort']['golden_hour_compliance_pct']}%")
    print(f"  Ward Golden Hour Compliance (<=60m): {icu_comp['ward_cohort']['golden_hour_compliance_pct']}%")

    print("\n--- Clinical Cohort Comparison Summary ---")
    print(metrics_df[["cohort_name", "patient_cases", "median_event_count", "median_duration_days", "antibiotic_admin_rate_pct", "readmission_rate_pct"]].to_string(index=False))

if __name__ == "__main__":
    main()
