"""Member 4 Dashboard Data Loader & Executive KPI Aggregator
Author: Tanisha Kumari (Member 4 - BI Dashboard Specialist)
Project: CareFlow: Clinical Pathway Process Mining
"""

from pathlib import Path
import json
import pandas as pd
import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parent.parent
STAR_DIR = PROJECT_ROOT / "reports" / "star_schema"
DASHBOARD_DIR = PROJECT_ROOT / "dashboard"

def load_star_schema_tables():
    """Load dimensional star-schema tables for dashboard consumption."""
    fact_path = STAR_DIR / "fact_clinical_events.csv"
    pat_path = STAR_DIR / "dim_patient_cohort.csv"
    act_path = STAR_DIR / "dim_activity.csv"
    dept_path = STAR_DIR / "dim_department.csv"
    time_path = STAR_DIR / "dim_time_bucket.csv"

    if not fact_path.exists():
        raise FileNotFoundError(f"Star-schema fact table missing at: {fact_path}")

    fact_df = pd.read_csv(fact_path)
    pat_df = pd.read_csv(pat_path)
    act_df = pd.read_csv(act_path)
    dept_df = pd.read_csv(dept_path)
    time_df = pd.read_csv(time_path)

    return fact_df, pat_df, act_df, dept_df, time_df

def aggregate_dashboard_kpis(fact_df, pat_df, act_df, dept_df, time_df):
    """Aggregate core executive KPI cards and archetype metrics for Power BI and Streamlit."""
    DASHBOARD_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Executive Headline Cards
    total_patients = int(len(pat_df))
    total_events = int(len(fact_df))
    unique_activities = int(len(act_df))
    unique_departments = int(len(dept_df))

    # Sepsis Golden Hour SLA (IV Antibiotics)
    abx_act_key = act_df[act_df["activity_name"] == "IV Antibiotics"]["activity_key"].iloc[0]
    abx_facts = fact_df[fact_df["activity_key"] == abx_act_key]
    abx_total = len(abx_facts)
    abx_delayed = int(abx_facts["is_sla_delayed"].sum())
    golden_hour_compliance_pct = round((1.0 - (abx_delayed / abx_total)) * 100.0, 2) if abx_total > 0 else 0.0

    # Readmissions
    readmissions = int(pat_df["has_readmission"].sum())
    readmission_rate_pct = round((readmissions / total_patients) * 100.0, 2)

    # Median Length of Stay
    median_los_days = round(float(pat_df["total_stay_days"].median()), 2)
    mean_los_days = round(float(pat_df["total_stay_days"].mean()), 2)

    # Central Lab Workload Share
    lab_dept_key = dept_df[dept_df["org_code"] == "B"]["department_key"].iloc[0]
    lab_events = int((fact_df["department_key"] == lab_dept_key).sum())
    lab_workload_share_pct = round((lab_events / total_events) * 100.0, 2)

    kpi_cards = [
        {"kpi_name": "Total Patient Encounters", "metric_value": f"{total_patients:,}", "category": "Volume", "target_benchmark": "1,050 Cohort"},
        {"kpi_name": "Total Clinical Transitions", "metric_value": f"{total_events:,}", "category": "Volume", "target_benchmark": "15,213 Events"},
        {"kpi_name": "Sepsis Golden Hour Compliance", "metric_value": f"{golden_hour_compliance_pct}%", "category": "Clinical SLA", "target_benchmark": ">= 90.0% Target"},
        {"kpi_name": "Unplanned ER Readmission Rate", "metric_value": f"{readmission_rate_pct}%", "category": "Quality", "target_benchmark": "< 20.0% Benchmark"},
        {"kpi_name": "Median Length of Stay", "metric_value": f"{median_los_days} Days", "category": "Capacity", "target_benchmark": "< 5.0 Days"},
        {"kpi_name": "Central Lab Workload Share", "metric_value": f"{lab_workload_share_pct}%", "category": "Operations", "target_benchmark": "< 40.0% Balance"},
    ]
    kpi_df = pd.DataFrame(kpi_cards)

    # 2. Care Archetype Aggregation
    archetype_summary = pat_df.groupby("care_archetype").agg(
        patient_count=("patient_cohort_key", "count"),
        median_stay_days=("total_stay_days", "median"),
        mean_stay_days=("total_stay_days", "mean"),
        readmissions=("has_readmission", "sum"),
        icu_admissions=("has_icu_admission", "sum"),
        geriatric_patients=("is_geriatric", "sum"),
    ).reset_index()

    archetype_summary["population_share_pct"] = (
        archetype_summary["patient_count"] / total_patients * 100.0
    ).round(2)
    archetype_summary["readmission_rate_pct"] = (
        archetype_summary["readmissions"] / archetype_summary["patient_count"] * 100.0
    ).round(2)

    # Export to CSVs for Power BI / Dashboard ingestion
    kpi_csv = DASHBOARD_DIR / "dashboard_kpi_cards.csv"
    kpi_df.to_csv(kpi_csv, index=False)
    print(f"Exported Dashboard KPI Cards CSV: {kpi_csv}")

    archetype_csv = DASHBOARD_DIR / "dashboard_archetype_metrics.csv"
    archetype_summary.to_csv(archetype_csv, index=False)
    print(f"Exported Dashboard Archetype Metrics CSV: {archetype_csv}")

    summary = {
        "dashboard_title": "CareFlow Executive Overview Dashboard",
        "author": "Tanisha Kumari (Member 4)",
        "headline_kpis": {row["kpi_name"]: row["metric_value"] for row in kpi_cards},
        "care_archetypes": archetype_summary.to_dict(orient="records"),
    }

    summary_json = DASHBOARD_DIR / "dashboard_summary.json"
    with open(summary_json, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    print(f"Exported Dashboard Summary JSON: {summary_json}")

    return kpi_df, archetype_summary, summary

def main():
    print("Loading Star-Schema data warehouse tables for Member 4 dashboard...")
    fact_df, pat_df, act_df, dept_df, time_df = load_star_schema_tables()
    kpi_df, arch_df, summary = aggregate_dashboard_kpis(fact_df, pat_df, act_df, dept_df, time_df)

    print("\n--- Member 4 Dashboard Executive Cards ---")
    for _, row in kpi_df.iterrows():
        print(f"  {row['kpi_name']}: {row['metric_value']} ({row['category']})")
    print("\nDashboard data loading finished successfully.")

if __name__ == "__main__":
    main()
