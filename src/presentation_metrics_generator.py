"""CareFlow Final Presentation Slide Metrics & Executive Defense Aggregator
Author: Amit Prajapati (Member 3 - Process Mining Analyst)
Project: CareFlow: Clinical Pathway Process Mining
"""

from pathlib import Path
import json
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as patches

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

def plot_milestone_roadmap(output_dir=OUTPUT_DIR):
    """Generate high-resolution 4-week analytical pipeline milestone roadmap diagram."""
    output_dir.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(16, 8), dpi=200)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis("off")

    phases = [
        {
            "week": "WEEK 1 (Days 1 - 5)",
            "title": "Data Hygiene, Discovery & SLAs",
            "color": "#2980b9",
            "items": [
                "• 15,213 Events & 1,050 Cases Ingestion",
                "• Resolved 4,446 Same-Second Ties",
                "• PM4Py DFG Mining: Happy Path vs Spaghetti",
                "• Sepsis Golden Hour SLA (84.8% on-time)",
                "• Transition Duration Matrix & Rework Loops",
            ],
            "x": 3, "y": 18, "w": 21, "h": 66,
        },
        {
            "week": "WEEK 2 (Days 6 - 10)",
            "title": "Formal Models & Archetypes",
            "color": "#8e44ad",
            "items": [
                "• Inductive Miner Workflow Petri Net",
                "• 39 Places, 50 Transitions, 116 Arcs",
                "• Causal Heuristic Net (D >= 0.5)",
                "• 691 Variants Clustered into 3 Archetypes:",
                "  - Rapid ER: 21.1% (Stay 45m, 0% readmit)",
                "  - Ward Acute: 46.0% (Stay 4.8d, 8.9% readmit)",
                "  - Critical ICU: 33.0% (Stay 44.7d, 72.5% readmit)",
            ],
            "x": 27, "y": 18, "w": 21, "h": 66,
        },
        {
            "week": "WEEK 3 (Days 11 - 15)",
            "title": "Conformance & Lab Queueing",
            "color": "#16a085",
            "items": [
                "• Token-Based Replay Simulation Engine",
                "• 100.0% Replay Fitness (p=c=49,273 tokens)",
                "• 0 Missing & 0 Remaining Tokens",
                "• Central Lab B Workload (53.31% Events)",
                "• Lab Turnaround Tails (Median 24.5m, p90 49.6m)",
                "• Ward-to-ICU Escalation Latency (5.01h)",
            ],
            "x": 51, "y": 18, "w": 21, "h": 66,
        },
        {
            "week": "WEEK 4 (Days 16 - 20)",
            "title": "Readmission, DW & CDSS",
            "color": "#d35400",
            "items": [
                "• Readmission Root-Cause Mining (28.0% Rate)",
                "• Stay >=7d Risk Multiplier (OR = 104.96)",
                "• Repeat Blood Draws Instability (OR = 7.57)",
                "• Enterprise Star-Schema DW (15,213 Facts)",
                "• CDSS 10-point SPES Triage Scoring Engine",
                "• 543 High-Risk Escalations Flagged (<=30m abx)",
            ],
            "x": 75, "y": 18, "w": 22, "h": 66,
        },
    ]

    for p in phases:
        # Box background
        rect = patches.FancyBboxPatch(
            (p["x"], p["y"]), p["w"], p["h"],
            boxstyle="round,pad=0.5,rounding_size=1.5",
            facecolor="#fcfdfd", edgecolor="#2c3e50", linewidth=1.5
        )
        ax.add_patch(rect)

        # Header banner
        h_rect = patches.FancyBboxPatch(
            (p["x"], p["y"] + p["h"] - 8), p["w"], 8,
            boxstyle="round,pad=0.2,rounding_size=1.0",
            facecolor=p["color"], edgecolor="#2c3e50", linewidth=1.2
        )
        ax.add_patch(h_rect)

        # Header texts
        ax.text(p["x"] + p["w"] / 2, p["y"] + p["h"] - 3, p["week"],
                ha="center", va="center", color="white", fontsize=9.5, fontweight="bold")
        ax.text(p["x"] + p["w"] / 2, p["y"] + p["h"] - 6, p["title"],
                ha="center", va="center", color="#ecf0f1", fontsize=8.0, fontweight="bold")

        # Bullet points
        line_y = p["y"] + p["h"] - 12
        for item in p["items"]:
            weight = "bold" if ("Archetype" in item or "Replay Fitness" in item or "Star-Schema" in item or "OR =" in item) else "normal"
            color = "#c0392b" if "OR =" in item else ("#2c3e50" if weight == "normal" else "#1a252f")
            ax.text(p["x"] + 1.2, line_y, item, ha="left", va="center", fontsize=7.5, fontweight=weight, color=color)
            line_y -= 4.2

    # Draw Connecting Milestone Arrows
    for i in range(3):
        x1 = phases[i]["x"] + phases[i]["w"]
        x2 = phases[i+1]["x"]
        y_mid = 51
        ax.annotate(
            "", xy=(x2, y_mid), xytext=(x1, y_mid),
            arrowprops=dict(arrowstyle="-|>", color="#2c3e50", lw=2.5, mutation_scale=18)
        )

    # Title & Subtitle Banners
    ax.text(50, 95, "CareFlow: 4-Week End-to-End Clinical Process Mining Milestone Roadmap",
            ha="center", va="center", fontsize=13, fontweight="bold", color="#1a252f")
    ax.text(50, 91, "Member 3 (Process Mining Analyst) Deliverables | 1,050 Sepsis Patients, 15,213 Events, 100% Soundness",
            ha="center", va="center", fontsize=9, color="#7f8c8d")

    plt.tight_layout()
    chart_path = output_dir / "careflow_executive_milestone_roadmap.png"
    plt.savefig(chart_path, dpi=200, bbox_inches="tight")
    plt.close()
    print(f"Exported CareFlow Milestone Roadmap Diagram: {chart_path}")
    return chart_path

def main():
    print("Compiling slide-by-slide executive metrics for final defense...")
    bundle = generate_slide_metrics()
    plot_milestone_roadmap()
    print(f"Successfully compiled {bundle['total_slides']} slide metrics for CareFlow Final Defense.")

if __name__ == "__main__":
    main()
