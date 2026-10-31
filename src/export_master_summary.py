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
        "milestone": "Mid-Project Review & Advanced Pathway Mining (Day 16)",
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
            "petri_net_token_replay_fitness_pct": 100.0,
            "total_tokens_conserved": 49273,
            "missing_or_remaining_tokens": 0,
        },
        "care_archetypes": {
            "archetype_1_rapid_er": {"prevalence_pct": 21.05, "cases": 221, "median_stay_days": 0.03, "readmission_pct": 0.0},
            "archetype_2_inpatient_ward": {"prevalence_pct": 46.00, "cases": 483, "median_stay_days": 4.85, "readmission_pct": 8.9},
            "archetype_3_critical_icu": {"prevalence_pct": 32.95, "cases": 346, "median_stay_days": 44.70, "readmission_pct": 72.5},
        },
        "inter_ward_transfer_latencies": {
            "er_to_normal_ward": {"median_hours": 1.60, "p90_hours": 4.57, "cases": 19},
            "ward_to_icu_escalation": {"median_hours": 5.01, "p90_hours": 13.82, "cases": 21},
            "icu_to_ward_stepdown": {"median_hours": 7.35, "p90_hours": 14.64, "cases": 4},
            "ward_routine_discharge": {"median_hours": 67.74, "p90_hours": 124.20, "cases": 117},
        },
        "diagnostic_turnaround_times": {
            "crp": {"median_min": 24.30, "p90_min": 46.60, "within_60m_pct": 95.16, "repeat_rate_pct": 68.72},
            "leucocytes": {"median_min": 24.41, "p90_min": 46.64, "within_60m_pct": 95.14, "repeat_rate_pct": 66.90},
            "lactic_acid": {"median_min": 24.97, "p90_min": 49.55, "within_60m_pct": 93.77, "repeat_rate_pct": 20.00},
        },
        "readmission_risk_odds_ratios": {
            "extended_stay_ge_7_days": {"odds_ratio": 104.96, "readmit_rate_exposed_pct": 63.82, "readmit_rate_unexposed_pct": 1.65},
            "repeat_lab_orders_ge_2": {"odds_ratio": 7.57, "readmit_rate_exposed_pct": 37.40, "readmit_rate_unexposed_pct": 7.32},
            "sirs_criteria_ge_2": {"odds_ratio": 2.61, "readmit_rate_exposed_pct": 31.07, "readmit_rate_unexposed_pct": 14.72},
            "icu_admission": {"odds_ratio": 2.09, "readmit_rate_exposed_pct": 42.73, "readmit_rate_unexposed_pct": 26.28},
            "geriatric_age_ge_65": {"odds_ratio": 1.85, "readmit_rate_exposed_pct": 31.22, "readmit_rate_unexposed_pct": 19.73},
            "sepsis_sla_delayed_gt_60m": {"odds_ratio": 1.45, "readmit_rate_exposed_pct": 31.61, "readmit_rate_unexposed_pct": 24.17},
        },
        "top_clinical_bottlenecks": [
            {"step": "Admission NC -> Admission IC", "median_delay_hours": 5.01, "severity": "High (ICU Escalation Latency)"},
            {"step": "Admission IC -> Admission NC", "median_delay_hours": 7.35, "severity": "Moderate (Step-Down Bed Wait)"},
            {"step": "CRP -> CRP (Repeat Lab)", "median_delay_hours": 24.0, "severity": "Routine Inpatient Cycle (68.7% Patients)"},
            {"step": "Leucocytes -> Leucocytes", "median_delay_hours": 24.0, "severity": "Routine Inpatient Cycle (66.9% Patients)"},
            {"step": "ER Sepsis Triage -> IV Antibiotics", "median_delay_hours": 0.73, "severity": "Clinical SLA Target: <=1.0h (15.2% Exceeding)"},
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
