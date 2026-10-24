"""CareFlow Clinical Pathway Conformance Checking Module
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

def load_events():
    with sqlite3.connect(DB_PATH) as conn:
        df = pd.read_sql_query(
            """
            SELECT case_id, activity, event_time
            FROM events_analysis
            ORDER BY case_id, event_time ASC
            """,
            conn,
        )
    df["event_time"] = pd.to_datetime(df["event_time"], utc=True)
    return df

def check_pathway_conformance(df):
    """Evaluate observed patient pathways against normative hospital clinical guidelines."""
    case_groups = df.groupby("case_id")
    results = []

    for case_id, group in case_groups:
        acts = group["activity"].tolist()
        
        has_reg = "ER Registration" in acts
        has_triage = "ER Triage" in acts
        has_sepsis_triage = "ER Sepsis Triage" in acts
        has_antibiotics = "IV Antibiotics" in acts
        has_return = "Return ER" in acts
        
        # Check order compliance
        reg_first = (acts[0] == "ER Registration") if acts else False
        triage_before_sepsis = False
        if has_triage and has_sepsis_triage:
            idx_triage = acts.index("ER Triage")
            idx_sepsis = acts.index("ER Sepsis Triage")
            triage_before_sepsis = (idx_triage < idx_sepsis)

        # Standard clinical compliance points (out of 4 core milestones)
        score = sum([has_reg, has_triage, has_sepsis_triage, has_antibiotics])
        compliance_pct = (score / 4.0) * 100.0

        deviations = []
        if not has_reg:
            deviations.append("Missing ER Registration")
        elif not reg_first:
            deviations.append("ER Registration not first event")
        if not has_triage:
            deviations.append("Bypassed General Triage")
        if not has_sepsis_triage:
            deviations.append("Bypassed Sepsis Triage")
        if not triage_before_sepsis and has_triage and has_sepsis_triage:
            deviations.append("Sepsis Triage executed before General Triage")
        if not has_antibiotics:
            deviations.append("No IV Antibiotics Recorded")
        if has_return:
            deviations.append("ER Readmission Occurred")

        results.append({
            "case_id": case_id,
            "total_events": len(acts),
            "compliance_score_pct": compliance_pct,
            "has_registration": has_reg,
            "has_triage": has_triage,
            "has_sepsis_triage": has_sepsis_triage,
            "has_iv_antibiotics": has_antibiotics,
            "has_return_er": has_return,
            "deviations_count": len(deviations),
            "deviation_reasons": "; ".join(deviations) if deviations else "Fully Compliant",
        })

    conf_df = pd.DataFrame(results)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    conf_df.to_csv(REPORTS_DIR / "conformance_report.csv", index=False)
    print(f"Exported conformance report: {REPORTS_DIR / 'conformance_report.csv'}")
    return conf_df

def plot_conformance_distribution(conf_df):
    """Plot distribution of clinical pathway compliance scores."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    plt.figure(figsize=(10, 6))

    scores = conf_df["compliance_score_pct"].value_counts().sort_index()
    labels = [f"{int(k)}% Milestones" for k in scores.index]

    bars = plt.bar(labels, scores.values, color="#16a085", edgecolor="black", alpha=0.85)

    plt.title("Clinical Pathway Guideline Conformance Score Across Patients", fontsize=12, fontweight="bold")
    plt.xlabel("Pathway Compliance Milestone Score", fontsize=10, fontweight="bold")
    plt.ylabel("Number of Patient Cases", fontsize=10, fontweight="bold")

    for bar in bars:
        h = bar.get_height()
        pct = (h / len(conf_df)) * 100
        plt.annotate(
            f"{int(h)} ({pct:.1f}%)",
            xy=(bar.get_x() + bar.get_width() / 2, h),
            xytext=(0, 3),
            textcoords="offset points",
            ha="center",
            va="bottom",
            fontsize=9,
            fontweight="bold",
        )

    plt.tight_layout()
    out_plot = OUTPUT_DIR / "conformance_distribution.png"
    plt.savefig(out_plot, dpi=200)
    plt.close()
    print(f"Saved conformance chart: {out_plot}")

def main():
    print("Loading events for conformance checking...")
    df = load_events()
    conf_df = check_pathway_conformance(df)
    plot_conformance_distribution(conf_df)

    mean_comp = conf_df["compliance_score_pct"].mean()
    print(f"Mean Guideline Compliance Score: {mean_comp:.1f}%")
    print("Conformance checking completed successfully.")

if __name__ == "__main__":
    main()
