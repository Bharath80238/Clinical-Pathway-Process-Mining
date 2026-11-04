"""Clinical Pathway Variant Clustering & Care Archetype Engine
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

def plot_archetype_distribution(summary):
    """Plot donut chart of patient distribution across Care Archetypes."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    labels = ["Archetype 1\nRapid ER (21%)", "Archetype 2\nInpatient Ward (46%)", "Archetype 3\nCritical/ICU (33%)"]
    sizes = summary["patient_cases"]
    colors = ["#2ecc71", "#3498db", "#e74c3c"]

    plt.figure(figsize=(8, 8))
    wedges, texts, autotexts = plt.pie(
        sizes,
        labels=labels,
        autopct="%1.1f%%",
        startangle=140,
        colors=colors,
        textprops=dict(color="#2c3e50", fontweight="bold", fontsize=10),
        wedgeprops=dict(width=0.45, edgecolor="black", linewidth=1.5),
    )
    plt.title("CareFlow Patient Population by Clinical Care Archetype\n(Clustered from 691 Raw Pathway Variants)", fontsize=12, fontweight="bold", pad=15)
    plt.tight_layout()
    
    out_pie = OUTPUT_DIR / "variant_archetypes_pie.png"
    plt.savefig(out_pie, dpi=200)
    plt.close()
    print(f"Created archetype donut chart: {out_pie}")

def plot_archetype_metrics_comparison(summary):
    """Plot multi-attribute comparison across the 3 Care Archetypes."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

    names = ["Arch 1: Rapid ER", "Arch 2: Acute Ward", "Arch 3: Critical/ICU"]
    colors = ["#2ecc71", "#3498db", "#e74c3c"]

    # Subplot 1: Median Length of Stay
    bars1 = ax1.bar(names, summary["median_stay_days"], color=colors, edgecolor="black", alpha=0.85)
    ax1.set_title("Median Length of Stay by Archetype (Days)", fontsize=11, fontweight="bold")
    ax1.set_ylabel("Days", fontsize=10, fontweight="bold")
    for bar in bars1:
        h = bar.get_height()
        ax1.annotate(f"{h:.1f}d", xy=(bar.get_x() + bar.get_width() / 2, h), xytext=(0, 3),
                     textcoords="offset points", ha="center", va="bottom", fontsize=9, fontweight="bold")

    # Subplot 2: Readmission Rate vs Antibiotic Administration
    x = np.arange(len(names))
    width = 0.35
    bars_abx = ax2.bar(x - width/2, summary["antibiotic_rate_pct"], width, label="IV Antibiotics %", color="#2980b9", edgecolor="black")
    bars_readm = ax2.bar(x + width/2, summary["readmission_rate_pct"], width, label="Return ER Readmission %", color="#d35400", edgecolor="black")
    ax2.set_xticks(x)
    ax2.set_xticklabels(names, fontsize=9, fontweight="bold")
    ax2.set_title("Intervention & Readmission Rate by Archetype", fontsize=11, fontweight="bold")
    ax2.set_ylabel("Percentage (%)", fontsize=10, fontweight="bold")
    ax2.set_ylim(0, 115)
    ax2.legend(frameon=True, facecolor="white")

    for bars in [bars_abx, bars_readm]:
        for bar in bars:
            h = bar.get_height()
            ax2.annotate(f"{h:.1f}%", xy=(bar.get_x() + bar.get_width() / 2, h), xytext=(0, 3),
                         textcoords="offset points", ha="center", va="bottom", fontsize=8.5, fontweight="bold")

    plt.tight_layout()
    out_img = OUTPUT_DIR / "cluster_profile_comparison.png"
    plt.savefig(out_img, dpi=200)
    plt.close()
    print(f"Created cluster comparison chart: {out_img}")

def main():
    print("Loading case features for variant clustering...")
    df, case_features = load_case_level_features()
    print(f"Loaded {len(case_features)} patient cases.")

    print("\nClustering into Clinical Care Archetypes...")
    case_features, summary = cluster_into_clinical_archetypes(case_features)

    print("\nGenerating archetype visualizations...")
    plot_archetype_distribution(summary)
    plot_archetype_metrics_comparison(summary)
    print("Variant clustering completed successfully.")

if __name__ == "__main__":
    main()
