"""Clinical Pathway Variant Clustering & Care Archetype Engine
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

def load_case_level_features():
    """Extract multi-dimensional behavioral features per patient case."""
    with sqlite3.connect(DB_PATH) as conn:
        df = pd.read_sql_query(
            """
            SELECT case_id, activity, event_time, org_group, age, infection_suspected, sirs_criteria_2_or_more
            FROM events_analysis
            ORDER BY case_id, event_time ASC
            """,
            conn,
        )

    df["event_time"] = pd.to_datetime(df["event_time"], utc=True)

    case_features = df.groupby("case_id").agg(
        start_time=("event_time", "min"),
        end_time=("event_time", "max"),
        event_count=("activity", "count"),
        unique_activities=("activity", "nunique"),
        age=("age", "first"),
        infection_suspected=("infection_suspected", "first"),
        sirs_high_risk=("sirs_criteria_2_or_more", "first"),
        activities=("activity", lambda x: list(x)),
    ).reset_index()

    case_features["duration_days"] = (
        (case_features["end_time"] - case_features["start_time"]).dt.total_seconds() / 86400.0
    ).round(2)

    case_features["has_abx"] = case_features["activities"].apply(lambda acts: "IV Antibiotics" in acts)
    case_features["has_icu"] = case_features["activities"].apply(lambda acts: "Admission IC" in acts)
    case_features["has_nc"] = case_features["activities"].apply(lambda acts: "Admission NC" in acts)
    case_features["has_return_er"] = case_features["activities"].apply(lambda acts: "Return ER" in acts)
    case_features["has_release"] = case_features["activities"].apply(lambda acts: any(a.startswith("Release") for a in acts))

    return df, case_features

def cluster_into_clinical_archetypes(case_features):
    """Segment 691 raw pathway variants into 3 actionable Clinical Care Archetypes."""
    def assign_archetype(row):
        # Archetype 3: Critical Care / Complex ICU & Long Stay
        if row["has_icu"] or row["duration_days"] >= 15.0 or row["event_count"] >= 30:
            return "Archetype 3: Critical ICU Escalation & High-Complexity Care"
        # Archetype 1: Rapid ER Evaluation / Short Stay Outpatient
        elif row["duration_days"] < 1.0 and row["event_count"] <= 8 and not row["has_nc"]:
            return "Archetype 1: Rapid ER Evaluation & Same-Day Discharge"
        # Archetype 2: Standard Inpatient Acute Ward Recovery
        else:
            return "Archetype 2: Standard Inpatient Ward Acute Recovery"

    case_features["care_archetype"] = case_features.apply(assign_archetype, axis=1)

    # Compute summary profile per archetype
    summary = case_features.groupby("care_archetype").agg(
        patient_cases=("case_id", "count"),
        median_events=("event_count", "median"),
        mean_events=("event_count", "mean"),
        median_stay_days=("duration_days", "median"),
        mean_stay_days=("duration_days", "mean"),
        antibiotic_rate_pct=("has_abx", lambda x: round(x.mean() * 100, 2)),
        icu_rate_pct=("has_icu", lambda x: round(x.mean() * 100, 2)),
        readmission_rate_pct=("has_return_er", lambda x: round(x.mean() * 100, 2)),
        normal_discharge_rate_pct=("has_release", lambda x: round(x.mean() * 100, 2)),
        mean_age=("age", lambda x: round(x.mean(), 1)),
    ).reset_index()

    total_patients = len(case_features)
    summary["patient_share_pct"] = (summary["patient_cases"] / total_patients * 100).round(2)

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    out_csv = REPORTS_DIR / "variant_archetypes_summary.csv"
    summary.to_csv(out_csv, index=False)
    print(f"Exported care archetypes summary: {out_csv}")

    return case_features, summary

def main():
    print("Loading case features for variant clustering...")
    df, case_features = load_case_level_features()
    print(f"Loaded {len(case_features)} patient cases.")

    print("\nClustering into Clinical Care Archetypes...")
    case_features, summary = cluster_into_clinical_archetypes(case_features)
    
    print("\n--- Clinical Care Archetypes Profile ---")
    print(summary[["care_archetype", "patient_cases", "patient_share_pct", "median_events", "median_stay_days", "readmission_rate_pct"]].to_string(index=False))

if __name__ == "__main__":
    main()
