"""CareFlow Final Presentation Slide Metrics & Executive Defense Aggregator
Author: Amit Prajapati (Member 3 - Process Mining Analyst)
Project: CareFlow: Clinical Pathway Process Mining
"""

from pathlib import Path
import json
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent
REPORTS_DIR = PROJECT_ROOT / "reports"
OUTPUT_DIR = REPORTS_DIR / "figures" / "process_maps"

def generate_slide_metrics():
    """Compile presentation slide-by-slide executive KPI bundle for Final Project Defense."""
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    slides = [
        {
            "slide_number": 1,
            "slide_title": "Project Overview, Clinical Problem & Dataset Scope",
            "key_takeaway": "Analyzing 1,050 retrospective sepsis patient encounters comprising 15,213 discrete events across 16 clinical activities.",
            "metrics": [
                {"metric": "Total Patient Cohort", "value": "1,050 discrete cases"},
                {"metric": "Total Recorded Events", "value": "15,213 clinical events"},
                {"metric": "Unique Care Activities", "value": "16 clinical steps"},
                {"metric": "Timestamp Tie Resolution", "value": "4,446 events resolved (0 errors)"},
            ],
            "visual_artifact": "reports/figures/case_duration_distribution.png",
        },
        {
            "slide_number": 2,
            "slide_title": "Algorithmic Discovery: Happy Path vs. Spaghetti Reality",
            "key_takeaway": "Directly-Follows Graph (DFG) mining reduced 691 unmanageable trace variants into 3 actionable Care Archetypes.",
            "metrics": [
                {"metric": "Total Pathway Variants", "value": "691 distinct variants"},
                {"metric": "Archetype 1: Rapid ER", "value": "21.1% (median stay: 45 min, 0% readmissions)"},
                {"metric": "Archetype 2: Ward Care", "value": "46.0% (median stay: 4.85 days, 8.9% readmissions)"},
                {"metric": "Archetype 3: Critical ICU", "value": "33.0% (median stay: 44.7 days, 72.5% readmissions)"},
            ],
            "visual_artifact": "reports/figures/process_maps/happy_path.png",
        },
        {
            "slide_number": 3,
            "slide_title": "Sepsis Golden Hour SLA & Diagnostic Lab Bottlenecks",
            "key_takeaway": "84.8% of patients receive IV Antibiotics within 60 minutes; 15.2% breach the SLA due to 49.6-minute central lab turnaround tails.",
            "metrics": [
                {"metric": "Golden Hour SLA Compliance", "value": "84.8% (median: 44.0 minutes)"},
                {"metric": "Surviving Sepsis 3h Bundle", "value": "96.5% compliance"},
                {"metric": "Central Lab Workload Share", "value": "53.31% of hospital events (8,110 events)"},
                {"metric": "Biomarker Median TAT", "value": "24.3m (CRP), 24.4m (Leucocytes), 25.0m (LacticAcid)"},
            ],
            "visual_artifact": "reports/figures/process_maps/sepsis_golden_hour_sla.png",
        },
        {
            "slide_number": 4,
            "slide_title": "Mathematical Verification: Inductive Petri Net & Token Replay",
            "key_takeaway": "Proved 100.0% structural language acceptance and mathematical soundness across all 1,050 patient traces.",
            "metrics": [
                {"metric": "Petri Net Structure", "value": "39 Places, 50 Transitions, 116 Directed Arcs"},
                {"metric": "Produced / Consumed Tokens", "value": "p = c = 49,273 tokens conserved"},
                {"metric": "Missing / Remaining Tokens", "value": "m = 0, r = 0 (zero deadlocks)"},
                {"metric": "Mean Token Replay Fitness", "value": "1.0000 (100.0% perfect fitness)"},
            ],
            "visual_artifact": "reports/figures/process_maps/token_fitness_distribution.png",
        },
        {
            "slide_number": 5,
            "slide_title": "Unplanned Hospital Readmission Root-Cause Mining",
            "key_takeaway": "28.0% of sepsis patients return to the ER; extended hospitalization (>=7 days) multiplies readmission odds by 105x.",
            "metrics": [
                {"metric": "Baseline Readmission Rate", "value": "28.00% (294 returned patients)"},
                {"metric": "Extended Stay (>=7 Days) OR", "value": "Odds Ratio: 104.96 (63.8% vs 1.65%)"},
                {"metric": "Repeat Lab Tests (>=2 Draws) OR", "value": "Odds Ratio: 7.57 (37.4% vs 7.32%)"},
                {"metric": "Ward-to-ICU Escalation Delay", "value": "Median: 5.01 hours (p90: 13.82 hours)"},
            ],
            "visual_artifact": "reports/figures/process_maps/readmission_risk_factors.png",
        },
        {
            "slide_number": 6,
            "slide_title": "Star-Schema Data Warehouse & Clinical Decision Support (CDSS)",
            "key_takeaway": "Engineered an enterprise 5-table Star-Schema for Power BI and automated 10-point SPES triage scoring.",
            "metrics": [
                {"metric": "Star-Schema Fact Table", "value": "15,213 rows, 4 foreign keys (0 orphaned keys)"},
                {"metric": "Dimensional Hierarchy", "value": "4 dimensions (Cohort, Activity, Department, Time)"},
                {"metric": "High-Risk CDSS Escalations", "value": "543 patients (51.7%) flagged for stat <=30m abx"},
                {"metric": "Institutional Action Plan", "value": "POCT Lactic Acid, Decoupled Abx, Post-ICU Telehealth"},
            ],
            "visual_artifact": "reports/figures/process_maps/star_schema_entity_relationship.png",
        },
    ]

    bundle = {
        "presentation_title": "CareFlow: Clinical Pathway Process Mining Final Defense",
        "author": "Amit Prajapati (Member 3 — Process Mining Analyst)",
        "institutional_milestone": "Final Defense & Slide-Ready Metrics Package",
        "total_slides": len(slides),
        "slides": slides,
    }

    # Export JSON
    json_path = REPORTS_DIR / "final_defense_slide_kpis.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(bundle, f, indent=2)
    print(f"Exported Final Defense Slide KPIs JSON: {json_path}")

    # Export flat CSV table
    csv_rows = []
    for s in slides:
        for m in s["metrics"]:
            csv_rows.append({
                "slide_number": s["slide_number"],
                "slide_title": s["slide_title"],
                "key_takeaway": s["key_takeaway"],
                "metric_name": m["metric"],
                "metric_value": m["value"],
                "visual_artifact": s["visual_artifact"],
            })
    csv_df = pd.DataFrame(csv_rows)
    csv_path = REPORTS_DIR / "final_defense_metrics_table.csv"
    csv_df.to_csv(csv_path, index=False)
    print(f"Exported Final Defense Metrics Table CSV: {csv_path}")

    return bundle

def main():
    print("Compiling slide-by-slide executive metrics for final defense...")
    bundle = generate_slide_metrics()
    print(f"Successfully compiled {bundle['total_slides']} slide metrics for CareFlow Final Defense.")

if __name__ == "__main__":
    main()
