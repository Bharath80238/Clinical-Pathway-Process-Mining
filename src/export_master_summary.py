"""CareFlow Master Process Mining Data Bundle Generator
Author: Amit Prajapati (Member 3 - Process Mining Analyst)
Project: CareFlow: Clinical Pathway Process Mining
"""

from pathlib import Path
import json
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
REPORTS_DIR = PROJECT_ROOT / "reports"

def generate_master_summary():
    """Consolidate all process mining findings and KPIs into an executive bundle."""
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    summary = {
        "project": "CareFlow: Clinical Pathway Process Mining",
        "analyst": "Amit Prajapati (Member 3 - Process Mining Analyst)",
        "dataset": "Sepsis Cases Event Log (Eindhoven / MIMIC-aligned benchmark)",
        "milestone": "Week 1 Final Synthesis & Data Bundle",
        "executive_kpis": {
            "total_patient_cases": 1050,
            "total_recorded_events": 15213,
            "unique_clinical_activities": 16,
            "discovered_pathway_variants": 691,
            "overall_guideline_conformance_score_pct": 94.6,
            "unplanned_er_readmission_rate_pct": 28.0,
            "median_length_of_stay_days": 5.34,
            "median_trace_length_events": 13,
            "sepsis_antibiotics_golden_hour_compliance_pct": 84.8,
            "sepsis_antibiotics_three_hour_bundle_compliance_pct": 96.5,
        },
        "top_clinical_bottlenecks": [
            {"step": "Admission NC -> Admission IC", "median_delay_hours": 17.5, "severity": "High (ICU Escalation Delay)"},
            {"step": "Admission IC -> Admission NC", "median_delay_hours": 16.2, "severity": "Moderate (Step-Down Bed Wait)"},
            {"step": "CRP -> CRP (Repeat Lab)", "median_delay_hours": 24.0, "severity": "Routine Inpatient Cycle"},
            {"step": "Leucocytes -> Leucocytes", "median_delay_hours": 24.0, "severity": "Routine Inpatient Cycle"},
            {"step": "ER Sepsis Triage -> IV Antibiotics", "median_delay_hours": 0.75, "severity": "Clinical SLA Target: <=1.0h"},
        ],
        "workload_by_department": {
            "Central Diagnostic Laboratory (B)": "53.31% (8,110 events, 96.5% reach)",
            "Emergency Clinical Staff (A & L)": "24.16% (3,675 events, 95.2% reach)",
            "Emergency Triage Unit (C)": "6.92% (1,053 events, 100.0% reach)",
            "General Inpatient Wards (F, O, G, etc.)": "7.82% (1,189 events, 80.9% reach)",
            "Discharge Administration (E)": "5.14% (782 events, 74.5% reach)",
            "Emergency Readmission (?)": "1.93% (294 events, 28.0% reach)",
            "Intensive Care Units (P, W, J, K)": "0.72% (110 events, 10.5% reach)",
        },
        "cohort_comparison": {
            "infection_suspected": {"cases": 848, "median_stay_days": 6.37, "readmission_rate_pct": 31.01, "antibiotic_rate_pct": 95.87},
            "infection_not_suspected": {"cases": 202, "median_stay_days": 0.10, "readmission_rate_pct": 15.35, "antibiotic_rate_pct": 4.95},
            "icu_admitted": {"cases": 110, "median_stay_days": 19.84, "readmission_rate_pct": 42.73, "antibiotic_rate_pct": 90.91},
            "normal_ward_only": {"cases": 940, "median_stay_days": 4.91, "readmission_rate_pct": 26.28, "antibiotic_rate_pct": 76.91},
            "geriatric_age_65_plus": {"cases": 756, "median_stay_days": 6.29, "readmission_rate_pct": 31.22, "antibiotic_rate_pct": 81.35},
        },
    }

    out_json = REPORTS_DIR / "careflow_process_mining_master_summary.json"
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    print(f"Generated master process mining summary bundle: {out_json}")
    return summary

if __name__ == "__main__":
    generate_master_summary()
