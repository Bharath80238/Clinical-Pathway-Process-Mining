"""CareFlow Readmission Risk Factor & Clinical Root-Cause Mining Module
Author: Amit Prajapati (Member 3 - Process Mining Analyst)
Project: CareFlow: Clinical Pathway Process Mining
"""

from pathlib import Path
import sqlite3
import json
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = PROJECT_ROOT / "data" / "processed" / "careflow.db"
REPORTS_DIR = PROJECT_ROOT / "reports"
OUTPUT_DIR = REPORTS_DIR / "figures" / "process_maps"

def load_case_cohort_features(db_path=DB_PATH):
    """Extract clinical, operational, and pathway features per patient case."""
    if not Path(db_path).exists():
        raise FileNotFoundError(f"Database not found at: {db_path}")

    with sqlite3.connect(db_path) as conn:
        df = pd.read_sql_query(
            """
            SELECT case_id, activity, event_time, org_group, age, infection_suspected, sirs_criteria_2_or_more
            FROM events_analysis
            ORDER BY case_id, event_time ASC
            """,
            conn,
        )

    df["event_time"] = pd.to_datetime(df["event_time"], utc=True)

    # Aggregate to case-level features
    records = []
    for case_id, group in df.groupby("case_id"):
        acts = set(group["activity"])
        times = group["event_time"].tolist()
        
        # Clinical indicators
        age = float(group["age"].iloc[0]) if pd.notna(group["age"].iloc[0]) else 50.0
        infection = bool(group["infection_suspected"].iloc[0]) if pd.notna(group["infection_suspected"].iloc[0]) else False
        sirs = bool(group["sirs_criteria_2_or_more"].iloc[0]) if pd.notna(group["sirs_criteria_2_or_more"].iloc[0]) else False
        
        # Pathway flags
        has_readmit = int("Return ER" in acts)
        has_icu = int("Admission IC" in acts)
        has_ward = int("Admission NC" in acts)
        has_abx = int("IV Antibiotics" in acts)
        
        # Trace & stay duration
        event_count = len(group)
        los_days = (times[-1] - times[0]).total_seconds() / 86400.0
        
        # Lab repetition counts
        crp_cnt = int((group["activity"] == "CRP").sum())
        leuco_cnt = int((group["activity"] == "Leucocytes").sum())
        lactic_cnt = int((group["activity"] == "LacticAcid").sum())
        total_lab_events = crp_cnt + leuco_cnt + lactic_cnt
        has_repeat_labs = int(crp_cnt > 1 or leuco_cnt > 1 or lactic_cnt > 1)
        
        # Sepsis Golden Hour SLA (triage to abx)
        triage_rows = group[group["activity"].isin(["ER Registration", "ER Triage", "ER Sepsis Triage"])]
        abx_rows = group[group["activity"] == "IV Antibiotics"]
        abx_delayed = 0
        if len(triage_rows) > 0 and len(abx_rows) > 0:
            tat = (abx_rows["event_time"].iloc[0] - triage_rows["event_time"].iloc[0]).total_seconds() / 60.0
            if tat > 60:
                abx_delayed = 1

        records.append({
            "case_id": case_id,
            "has_readmit": has_readmit,
            "age": age,
            "is_geriatric": int(age >= 65),
            "infection_suspected": int(infection),
            "sirs_criteria": int(sirs),
            "has_icu": has_icu,
            "has_ward": has_ward,
            "has_abx": has_abx,
            "event_count": event_count,
            "los_days": round(los_days, 2),
            "is_long_stay": int(los_days >= 7.0),
            "crp_count": crp_cnt,
            "leucocytes_count": leuco_cnt,
            "lactic_count": lactic_cnt,
            "total_lab_events": total_lab_events,
            "has_repeat_labs": has_repeat_labs,
            "abx_delayed": abx_delayed,
        })

    return pd.DataFrame(records)

def calculate_odds_ratio(a, b, c, d):
    """Compute Odds Ratio and 95% Confidence Interval with Haldane-Anscombe correction."""
    # Contingency Table:
    # a: Exposed with Readmission, b: Exposed without Readmission
    # c: Unexposed with Readmission, d: Unexposed without Readmission
    if a == 0 or b == 0 or c == 0 or d == 0:
        a, b, c, d = a + 0.5, b + 0.5, c + 0.5, d + 0.5

    odds_ratio = (a * d) / (b * c)
    log_or = np.log(odds_ratio)
    se_log_or = np.sqrt(1.0/a + 1.0/b + 1.0/c + 1.0/d)
    ci_lower = np.exp(log_or - 1.96 * se_log_or)
    ci_upper = np.exp(log_or + 1.96 * se_log_or)
    return round(float(odds_ratio), 2), round(float(ci_lower), 2), round(float(ci_upper), 2)

def mine_readmission_risk_factors(case_df):
    """Compute relative risk, odds ratios, and readmission rates across clinical predictors."""
    predictors = [
        ("has_icu", "ICU Admission (Admission IC)", "Critical Care Escalation"),
        ("is_long_stay", "Extended Length of Stay (>= 7 Days)", "Prolonged Inpatient Treatment"),
        ("has_repeat_labs", "Repetitive Laboratory Orders (>= 2 Draws)", "Clinical Instability & Monitoring"),
        ("is_geriatric", "Geriatric Age Cohort (Age >= 65)", "Vulnerable Elderly Population"),
        ("sirs_criteria", "Systemic Inflammatory Response (SIRS >= 2)", "Severe Systemic Presentation"),
        ("abx_delayed", "Sepsis Golden Hour SLA Delay (> 60 Min)", "Delayed Antimicrobial Administration"),
        ("has_ward", "Normal Care Ward Admission (Admission NC)", "Inpatient Hospitalization"),
    ]

    total_patients = len(case_df)
    baseline_readmissions = int(case_df["has_readmit"].sum())
    baseline_rate = round((baseline_readmissions / total_patients) * 100.0, 2)

    risk_rows = []
    for col, name, category in predictors:
        exposed = case_df[case_df[col] == 1]
        unexposed = case_df[case_df[col] == 0]

        n_exposed = len(exposed)
        n_unexposed = len(unexposed)

        readmit_exposed = int(exposed["has_readmit"].sum())
        readmit_unexposed = int(unexposed["has_readmit"].sum())

        rate_exposed = round((readmit_exposed / n_exposed) * 100.0, 2) if n_exposed > 0 else 0.0
        rate_unexposed = round((readmit_unexposed / n_unexposed) * 100.0, 2) if n_unexposed > 0 else 0.0

        rel_risk = round(rate_exposed / rate_unexposed, 2) if rate_unexposed > 0 else 0.0
        risk_diff = round(rate_exposed - rate_unexposed, 2)

        # 2x2 contingency table
        a = readmit_exposed
        b = n_exposed - readmit_exposed
        c = readmit_unexposed
        d = n_unexposed - readmit_unexposed

        odds_ratio, ci_low, ci_high = calculate_odds_ratio(a, b, c, d)

        risk_rows.append({
            "predictor_feature": col,
            "predictor_name": name,
            "clinical_category": category,
            "exposed_count": n_exposed,
            "exposed_prevalence_pct": round((n_exposed / total_patients) * 100.0, 2),
            "readmissions_exposed": readmit_exposed,
            "readmission_rate_exposed_pct": rate_exposed,
            "unexposed_count": n_unexposed,
            "readmissions_unexposed": readmit_unexposed,
            "readmission_rate_unexposed_pct": rate_unexposed,
            "relative_risk": rel_risk,
            "risk_difference_pct": risk_diff,
            "odds_ratio": odds_ratio,
            "ci_95_lower": ci_low,
            "ci_95_upper": ci_high,
        })

    risk_df = pd.DataFrame(risk_rows).sort_values(by="odds_ratio", ascending=False)

    summary = {
        "total_cohort_patients": total_patients,
        "total_readmission_cases": baseline_readmissions,
        "baseline_readmission_rate_pct": baseline_rate,
        "primary_risk_factor": risk_df.iloc[0]["predictor_name"],
        "primary_odds_ratio": risk_df.iloc[0]["odds_ratio"],
        "risk_factors": risk_rows,
    }

    return risk_df, summary

def plot_readmission_risk_factors(risk_df, case_df, output_dir=OUTPUT_DIR):
    """Generate multi-panel readmission risk factor and clinical stratification plots."""
    output_dir.mkdir(parents=True, exist_ok=True)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

    # Filter out baseline admission which is an inclusion criterion, for focused clinical display
    plot_factors = risk_df[risk_df["predictor_feature"] != "has_ward"].copy()
    plot_factors = plot_factors.sort_values(by="odds_ratio", ascending=True)

    y_pos = np.arange(len(plot_factors))
    labels = plot_factors["predictor_name"]
    ors = plot_factors["odds_ratio"]

    # Panel 1: Odds Ratios with 95% Confidence Intervals (Log-Scale Horizontal Bar)
    bars1 = ax1.barh(y_pos, ors, color="#c0392b", edgecolor="black", alpha=0.85, height=0.55)
    ax1.set_yticks(y_pos)
    ax1.set_yticklabels(labels, fontsize=9, fontweight="bold")
    ax1.set_xscale("log")
    ax1.axvline(1.0, color="#7f8c8d", linestyle="--", linewidth=1.5, label="Neutral Risk (OR = 1.0)")
    ax1.set_xlabel("Odds Ratio (Logarithmic Scale)", fontsize=10, fontweight="bold")
    ax1.set_title("Clinical Risk Factors for Hospital Readmission (Return ER)", fontsize=11, fontweight="bold")
    ax1.grid(axis="x", linestyle="--", alpha=0.5)
    ax1.legend(loc="lower right", frameon=True, facecolor="white")

    for bar, (_, row) in zip(bars1, plot_factors.iterrows()):
        w = bar.get_width()
        ax1.annotate(
            f"OR: {w:.2f} [{row['ci_95_lower']}, {row['ci_95_upper']}]",
            xy=(w, bar.get_y() + bar.get_height() / 2),
            xytext=(6, 0),
            textcoords="offset points",
            va="center",
            fontsize=8.5,
            fontweight="bold",
        )

    # Panel 2: Readmission Rate Comparison (Exposed vs Unexposed Cohort)
    width = 0.35
    exp_rates = plot_factors["readmission_rate_exposed_pct"]
    unexp_rates = plot_factors["readmission_rate_unexposed_pct"]

    bars_exp = ax2.barh(y_pos + width/2, exp_rates, width, label="Factor Present (Exposed)", color="#e74c3c", edgecolor="black", alpha=0.85)
    bars_unexp = ax2.barh(y_pos - width/2, unexp_rates, width, label="Factor Absent (Unexposed)", color="#3498db", edgecolor="black", alpha=0.85)

    ax2.set_yticks(y_pos)
    ax2.set_yticklabels([""] * len(plot_factors))
    ax2.set_xlabel("Readmission Rate (% of Cohort Returning to ER)", fontsize=10, fontweight="bold")
    ax2.set_title("Readmission Incidence Comparison by Clinical Predictor", fontsize=11, fontweight="bold")
    ax2.grid(axis="x", linestyle="--", alpha=0.5)
    ax2.legend(loc="lower right", frameon=True, facecolor="white")

    for bar in bars_exp:
        w = bar.get_width()
        ax2.annotate(f"{w:.1f}%", xy=(w, bar.get_y() + bar.get_height() / 2), xytext=(4, 0), textcoords="offset points", va="center", fontsize=8, fontweight="bold")
    for bar in bars_unexp:
        w = bar.get_width()
        ax2.annotate(f"{w:.1f}%", xy=(w, bar.get_y() + bar.get_height() / 2), xytext=(4, 0), textcoords="offset points", va="center", fontsize=8, fontweight="bold")

    plt.tight_layout()
    chart_path = output_dir / "readmission_risk_factors.png"
    plt.savefig(chart_path, dpi=200)
    plt.close()
    print(f"Exported readmission risk chart: {chart_path}")
    return chart_path

def main():
    print("Loading patient cohort features for readmission root-cause analysis...")
    case_df = load_case_cohort_features()
    risk_df, summary = mine_readmission_risk_factors(case_df)

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    csv_path = REPORTS_DIR / "readmission_risk_factors.csv"
    risk_df.to_csv(csv_path, index=False)
    print(f"Exported readmission risk factors CSV: {csv_path}")

    json_path = REPORTS_DIR / "readmission_risk_summary.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    print(f"Exported readmission risk summary JSON: {json_path}")

    plot_readmission_risk_factors(risk_df, case_df)

    print("\n--- Readmission Root-Cause Risk Factors (Ranked by Odds Ratio) ---")
    for _, row in risk_df.iterrows():
        print(f"Predictor: {row['predictor_name']}")
        print(f"  Exposed Readmission Rate: {row['readmission_rate_exposed_pct']}% vs Unexposed: {row['readmission_rate_unexposed_pct']}%")
        print(f"  Odds Ratio: {row['odds_ratio']} (95% CI: [{row['ci_95_lower']}, {row['ci_95_upper']}])")

if __name__ == "__main__":
    main()
