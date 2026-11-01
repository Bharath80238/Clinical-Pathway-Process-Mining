"""CareFlow Dimensional Star-Schema Data Warehouse Model
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
import matplotlib.patches as patches

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = PROJECT_ROOT / "data" / "processed" / "careflow.db"
REPORTS_DIR = PROJECT_ROOT / "reports"
STAR_DIR = REPORTS_DIR / "star_schema"
FIGURES_DIR = REPORTS_DIR / "figures" / "process_maps"

def load_source_events(db_path=DB_PATH):
    """Load ordered events from SQLite."""
    if not Path(db_path).exists():
        raise FileNotFoundError(f"Database not found at: {db_path}")

    with sqlite3.connect(db_path) as conn:
        df = pd.read_sql_query(
            """
            SELECT case_id, activity, event_time, org_group, leucocytes, crp, lactic_acid,
                   age, infection_suspected, sirs_criteria_2_or_more, disfunc_org
            FROM events_analysis
            ORDER BY case_id, event_time ASC
            """,
            conn,
        )

    df["event_time"] = pd.to_datetime(df["event_time"], utc=True)
    return df

def build_star_schema(df):
    """Transform flat event log into an enterprise star-schema data warehouse model."""
    STAR_DIR.mkdir(parents=True, exist_ok=True)

    # ---------------------------------------------------------
    # 1. Dimension: dim_activity
    # ---------------------------------------------------------
    activities = sorted(df["activity"].unique())
    phase_map = {
        "ER Registration": "Intake & Registration",
        "ER Triage": "Emergency Triage",
        "ER Sepsis Triage": "Emergency Triage",
        "CRP": "Diagnostic Laboratory",
        "Leucocytes": "Diagnostic Laboratory",
        "LacticAcid": "Diagnostic Laboratory",
        "IV Antibiotics": "Therapeutic Intervention",
        "IV Liquid": "Therapeutic Intervention",
        "Admission NC": "Inpatient Ward Care",
        "Admission IC": "Critical Intensive Care",
        "Release A": "Discharge",
        "Release B": "Discharge",
        "Release C": "Discharge",
        "Release D": "Discharge",
        "Release E": "Discharge",
        "Return ER": "Emergency Readmission",
    }
    normative_flag = {
        act: 1 if act in ["ER Registration", "ER Triage", "ER Sepsis Triage", "CRP", "Leucocytes", "LacticAcid", "IV Antibiotics", "Admission NC", "Release A"] else 0
        for act in activities
    }

    dim_activity = pd.DataFrame({
        "activity_key": range(1, len(activities) + 1),
        "activity_name": activities,
        "clinical_phase": [phase_map.get(a, "Other") for a in activities],
        "is_normative_step": [normative_flag[a] for a in activities],
        "is_diagnostic_lab": [1 if a in ["CRP", "Leucocytes", "LacticAcid"] else 0 for a in activities],
        "is_admission_step": [1 if "Admission" in a else 0 for a in activities],
        "is_discharge_step": [1 if "Release" in a or "Return ER" in a else 0 for a in activities],
    })

    act_to_key = dict(zip(dim_activity["activity_name"], dim_activity["activity_key"]))

    # ---------------------------------------------------------
    # 2. Dimension: dim_department
    # ---------------------------------------------------------
    dept_map = {
        "A": ("Emergency Clinical Staff A", "Emergency Care", "Primary Clinical"),
        "B": ("Central Diagnostic Laboratory", "Diagnostics", "Ancillary Support"),
        "C": ("Emergency Triage Nursing", "Emergency Care", "Intake / Triage"),
        "E": ("Discharge Administration", "Administration", "Outpatient Transition"),
        "F": ("Internal Medicine Ward", "Inpatient Ward", "Secondary Care"),
        "G": ("General Surgery Ward", "Inpatient Ward", "Surgical Inpatient"),
        "H": ("Cardiology Ward", "Inpatient Ward", "Specialized Inpatient"),
        "I": ("Pulmonology Ward", "Inpatient Ward", "Specialized Inpatient"),
        "J": ("Pediatric / Specialty ICU", "Critical Care", "Tertiary Intensive"),
        "K": ("Neurosurgical ICU", "Critical Care", "Tertiary Intensive"),
        "L": ("Emergency Clinical Staff L", "Emergency Care", "Primary Clinical"),
        "M": ("Gastroenterology Ward", "Inpatient Ward", "Specialized Inpatient"),
        "N": ("Nephrology Ward", "Inpatient Ward", "Specialized Inpatient"),
        "O": ("Geriatric Inpatient Ward", "Inpatient Ward", "Subacute Inpatient"),
        "P": ("Medical Intensive Care Unit", "Critical Care", "Tertiary Intensive"),
        "Q": ("Oncology Ward", "Inpatient Ward", "Specialized Inpatient"),
        "R": ("Orthopedic Ward", "Inpatient Ward", "Surgical Inpatient"),
        "S": ("Neurology Ward", "Inpatient Ward", "Specialized Inpatient"),
        "T": ("Infectious Diseases Ward", "Inpatient Ward", "Specialized Inpatient"),
        "U": ("Urology Ward", "Inpatient Ward", "Surgical Inpatient"),
        "V": ("Vascular Surgery Ward", "Inpatient Ward", "Surgical Inpatient"),
        "W": ("Surgical Intensive Care Unit", "Critical Care", "Tertiary Intensive"),
        "X": ("Radiology & Imaging Unit", "Diagnostics", "Ancillary Support"),
        "Y": ("Post-Anesthesia Care Unit", "Perioperative", "Subacute Intensive"),
        "Z": ("Palliative Care Unit", "Inpatient Ward", "Supportive Care"),
        "?": ("External / Unassigned", "Unknown", "External Transfer"),
    }

    all_orgs = sorted(df["org_group"].fillna("?").unique())
    dim_dept_records = []
    for idx, org in enumerate(all_orgs, 1):
        name, dept, tier = dept_map.get(org, (f"Department {org}", "General Hospital", "Support"))
        dim_dept_records.append({
            "department_key": idx,
            "org_code": org,
            "department_name": name,
            "clinical_division": dept,
            "service_tier": tier,
            "is_critical_care": 1 if "Critical Care" in dept or "Intensive" in tier else 0,
            "is_diagnostic_unit": 1 if "Diagnostics" in dept else 0,
        })
    dim_department = pd.DataFrame(dim_dept_records)
    org_to_key = dict(zip(dim_department["org_code"], dim_department["department_key"]))

    # ---------------------------------------------------------
    # 3. Dimension: dim_patient_cohort
    # ---------------------------------------------------------
    cohort_records = []
    case_groups = df.groupby("case_id")
    for idx, (case_id, grp) in enumerate(case_groups, 1):
        acts = set(grp["activity"])
        times = grp["event_time"].tolist()
        age = float(grp["age"].iloc[0]) if pd.notna(grp["age"].iloc[0]) else 50.0
        inf = int(grp["infection_suspected"].iloc[0]) if pd.notna(grp["infection_suspected"].iloc[0]) else 0
        sirs = int(grp["sirs_criteria_2_or_more"].iloc[0]) if pd.notna(grp["sirs_criteria_2_or_more"].iloc[0]) else 0
        disfunc = int(grp["disfunc_org"].iloc[0]) if pd.notna(grp["disfunc_org"].iloc[0]) else 0

        has_readmit = 1 if "Return ER" in acts else 0
        has_icu = 1 if "Admission IC" in acts else 0
        has_ward = 1 if "Admission NC" in acts else 0
        has_abx = 1 if "IV Antibiotics" in acts else 0

        los_days = round((times[-1] - times[0]).total_seconds() / 86400.0, 2)
        event_cnt = len(grp)

        # Care Archetype
        if has_icu or los_days > 20.0:
            archetype = "Archetype 3: Critical ICU Escalation"
        elif has_ward:
            archetype = "Archetype 2: Standard Ward Recovery"
        else:
            archetype = "Archetype 1: Rapid ER Evaluation"

        # Age bracket
        if age < 40:
            age_bracket = "<40 Years"
        elif age < 65:
            age_bracket = "40-64 Years"
        elif age < 80:
            age_bracket = "65-79 Years"
        else:
            age_bracket = "80+ Years (Elderly)"

        cohort_records.append({
            "patient_cohort_key": idx,
            "case_id": case_id,
            "age": age,
            "age_bracket": age_bracket,
            "is_geriatric": 1 if age >= 65 else 0,
            "infection_suspected": inf,
            "sirs_criteria": sirs,
            "organ_dysfunction": disfunc,
            "care_archetype": archetype,
            "has_icu_admission": has_icu,
            "has_ward_admission": has_ward,
            "has_antibiotics": has_abx,
            "has_readmission": has_readmit,
            "total_stay_days": los_days,
            "total_event_count": event_cnt,
            "is_extended_stay": 1 if los_days >= 7.0 else 0,
        })
    dim_patient_cohort = pd.DataFrame(cohort_records)
    case_to_key = dict(zip(dim_patient_cohort["case_id"], dim_patient_cohort["patient_cohort_key"]))

    # ---------------------------------------------------------
    # 4. Dimension: dim_time_bucket
    # ---------------------------------------------------------
    time_buckets = [
        {"time_bucket_key": 1, "bucket_name": "Immediate (<= 15 min)", "min_minutes": 0, "max_minutes": 15, "sla_compliance_grade": "Optimal"},
        {"time_bucket_key": 2, "bucket_name": "Rapid (15 - 30 min)", "min_minutes": 15, "max_minutes": 30, "sla_compliance_grade": "Good"},
        {"time_bucket_key": 3, "bucket_name": "Standard SLA (30 - 60 min)", "min_minutes": 30, "max_minutes": 60, "sla_compliance_grade": "Compliant"},
        {"time_bucket_key": 4, "bucket_name": "Delayed (60 - 180 min)", "min_minutes": 60, "max_minutes": 180, "sla_compliance_grade": "Breached (Mild)"},
        {"time_bucket_key": 5, "bucket_name": "Prolonged (> 180 min)", "min_minutes": 180, "max_minutes": 999999, "sla_compliance_grade": "Breached (Critical)"},
    ]
    dim_time_bucket = pd.DataFrame(time_buckets)

    def get_time_bucket(minutes):
        if pd.isna(minutes) or minutes < 0:
            return 1
        if minutes <= 15:
            return 1
        elif minutes <= 30:
            return 2
        elif minutes <= 60:
            return 3
        elif minutes <= 180:
            return 4
        else:
            return 5

    # ---------------------------------------------------------
    # 5. Fact Table: fact_clinical_events
    # ---------------------------------------------------------
    df_sorted = df.sort_values(by=["case_id", "event_time"]).copy()
    df_sorted["prev_time"] = df_sorted.groupby("case_id")["event_time"].shift(1)
    df_sorted["prev_activity"] = df_sorted.groupby("case_id")["activity"].shift(1)
    df_sorted["step_sequence"] = df_sorted.groupby("case_id").cumcount() + 1

    # Transition duration from previous step in minutes and hours
    df_sorted["transition_duration_minutes"] = (df_sorted["event_time"] - df_sorted["prev_time"]).dt.total_seconds() / 60.0
    df_sorted["transition_duration_minutes"] = df_sorted["transition_duration_minutes"].fillna(0.0).round(2)
    df_sorted["transition_duration_hours"] = (df_sorted["transition_duration_minutes"] / 60.0).round(2)

    # Time from case start
    case_start_times = df_sorted.groupby("case_id")["event_time"].transform("min")
    df_sorted["elapsed_from_start_hours"] = ((df_sorted["event_time"] - case_start_times).dt.total_seconds() / 3600.0).round(2)

    # Repeat activity flag (activity previously occurred in same case)
    df_sorted["activity_seen_count"] = df_sorted.groupby(["case_id", "activity"]).cumcount() + 1
    df_sorted["is_repeat_activity"] = (df_sorted["activity_seen_count"] > 1).astype(int)

    # Sepsis Golden Hour SLA target on IV Antibiotics
    df_sorted["is_sla_delayed"] = 0
    abx_mask = df_sorted["activity"] == "IV Antibiotics"
    df_sorted.loc[abx_mask & (df_sorted["elapsed_from_start_hours"] > 1.0), "is_sla_delayed"] = 1

    fact_records = []
    for idx, row in enumerate(df_sorted.itertuples(index=False), 1):
        org = row.org_group if pd.notna(row.org_group) else "?"
        p_key = case_to_key[row.case_id]
        a_key = act_to_key[row.activity]
        d_key = org_to_key.get(org, 1)
        t_key = get_time_bucket(row.transition_duration_minutes)

        fact_records.append({
            "event_surrogate_key": idx,
            "patient_cohort_key": p_key,
            "activity_key": a_key,
            "department_key": d_key,
            "time_bucket_key": t_key,
            "step_sequence": row.step_sequence,
            "timestamp": row.event_time.isoformat(),
            "transition_duration_minutes": row.transition_duration_minutes,
            "transition_duration_hours": row.transition_duration_hours,
            "elapsed_from_start_hours": row.elapsed_from_start_hours,
            "is_repeat_activity": row.is_repeat_activity,
            "is_sla_delayed": row.is_sla_delayed,
        })
    fact_clinical_events = pd.DataFrame(fact_records)

    # Export to CSVs
    dim_activity.to_csv(STAR_DIR / "dim_activity.csv", index=False)
    dim_department.to_csv(STAR_DIR / "dim_department.csv", index=False)
    dim_patient_cohort.to_csv(STAR_DIR / "dim_patient_cohort.csv", index=False)
    dim_time_bucket.to_csv(STAR_DIR / "dim_time_bucket.csv", index=False)
    fact_clinical_events.to_csv(STAR_DIR / "fact_clinical_events.csv", index=False)

    # Export to unified SQLite Data Warehouse
    dw_db_path = STAR_DIR / "careflow_star_schema.db"
    with sqlite3.connect(dw_db_path) as conn:
        dim_activity.to_sql("dim_activity", conn, if_exists="replace", index=False)
        dim_department.to_sql("dim_department", conn, if_exists="replace", index=False)
        dim_patient_cohort.to_sql("dim_patient_cohort", conn, if_exists="replace", index=False)
        dim_time_bucket.to_sql("dim_time_bucket", conn, if_exists="replace", index=False)
        fact_clinical_events.to_sql("fact_clinical_events", conn, if_exists="replace", index=False)

    summary = {
        "data_warehouse_name": "CareFlow Dimensional Star Schema",
        "fact_table": {
            "name": "fact_clinical_events",
            "total_rows": len(fact_clinical_events),
            "foreign_keys": ["patient_cohort_key", "activity_key", "department_key", "time_bucket_key"],
        },
        "dimension_tables": [
            {"name": "dim_activity", "rows": len(dim_activity)},
            {"name": "dim_department", "rows": len(dim_department)},
            {"name": "dim_patient_cohort", "rows": len(dim_patient_cohort)},
            {"name": "dim_time_bucket", "rows": len(dim_time_bucket)},
        ],
        "export_paths": {
            "sqlite_database": str(dw_db_path),
            "csv_directory": str(STAR_DIR),
        },
    }

    with open(REPORTS_DIR / "star_schema_summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    print(f"Constructed Star-Schema Data Warehouse in: {STAR_DIR}")
    print(f"  Fact rows: {len(fact_clinical_events):,}")
    print(f"  Patient cohort dim: {len(dim_patient_cohort):,} rows")
    print(f"  Activity dim: {len(dim_activity)} rows")
    print(f"  Department dim: {len(dim_department)} rows")
    return summary

def plot_star_schema_architecture(output_dir=FIGURES_DIR):
    """Draw a clean publication-grade entity-relationship star-schema architecture diagram."""
    output_dir.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(15, 9), dpi=200)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis("off")

    def draw_table_card(ax, x, y, width, height, title, fields, header_color, bg_color="#f8f9fa"):
        # Outer box
        rect = patches.FancyBboxPatch(
            (x, y), width, height,
            boxstyle="round,pad=0.5,rounding_size=1.5",
            facecolor=bg_color, edgecolor="#2c3e50", linewidth=1.5
        )
        ax.add_patch(rect)
        # Header banner
        header_h = 3.5
        h_rect = patches.FancyBboxPatch(
            (x, y + height - header_h), width, header_h,
            boxstyle="round,pad=0.2,rounding_size=1.0",
            facecolor=header_color, edgecolor="#2c3e50", linewidth=1.2
        )
        ax.add_patch(h_rect)
        # Title text
        ax.text(x + width / 2, y + height - header_h / 2, title,
                ha="center", va="center", color="white", fontsize=9.5, fontweight="bold")
        # Field items
        line_y = y + height - header_h - 2.0
        for field, is_pk, is_fk in fields:
            prefix = "[PK] " if is_pk else ("[FK] " if is_fk else "  • ")
            weight = "bold" if (is_pk or is_fk) else "normal"
            color = "#c0392b" if is_pk else ("#2980b9" if is_fk else "#2c3e50")
            ax.text(x + 1.5, line_y, f"{prefix}{field}", ha="left", va="center",
                    fontsize=8.0, fontweight=weight, color=color)
            line_y -= 2.0

    # Draw Central Fact Table
    fact_fields = [
        ("event_surrogate_key", True, False),
        ("patient_cohort_key", False, True),
        ("activity_key", False, True),
        ("department_key", False, True),
        ("time_bucket_key", False, True),
        ("step_sequence", False, False),
        ("timestamp", False, False),
        ("transition_duration_minutes", False, False),
        ("transition_duration_hours", False, False),
        ("elapsed_from_start_hours", False, False),
        ("is_repeat_activity", False, False),
        ("is_sla_delayed", False, False),
    ]
    draw_table_card(ax, 35, 30, 30, 34, "FACT_CLINICAL_EVENTS (15,213 rows)", fact_fields, "#e74c3c", "#fdfefe")

    # Dimension 1: dim_patient_cohort (Top-Left)
    pat_fields = [
        ("patient_cohort_key", True, False),
        ("case_id", False, False),
        ("age", False, False),
        ("age_bracket", False, False),
        ("is_geriatric", False, False),
        ("infection_suspected", False, False),
        ("sirs_criteria", False, False),
        ("care_archetype", False, False),
        ("has_icu_admission", False, False),
        ("has_readmission", False, False),
        ("total_stay_days", False, False),
    ]
    draw_table_card(ax, 3, 56, 26, 32, "DIM_PATIENT_COHORT (1,050 rows)", pat_fields, "#2980b9")

    # Dimension 2: dim_activity (Top-Right)
    act_fields = [
        ("activity_key", True, False),
        ("activity_name", False, False),
        ("clinical_phase", False, False),
        ("is_normative_step", False, False),
        ("is_diagnostic_lab", False, False),
        ("is_admission_step", False, False),
        ("is_discharge_step", False, False),
    ]
    draw_table_card(ax, 71, 62, 26, 24, "DIM_ACTIVITY (16 rows)", act_fields, "#27ae60")

    # Dimension 3: dim_department (Bottom-Left)
    dept_fields = [
        ("department_key", True, False),
        ("org_code", False, False),
        ("department_name", False, False),
        ("clinical_division", False, False),
        ("service_tier", False, False),
        ("is_critical_care", False, False),
    ]
    draw_table_card(ax, 3, 10, 26, 22, "DIM_DEPARTMENT (26 rows)", dept_fields, "#8e44ad")

    # Dimension 4: dim_time_bucket (Bottom-Right)
    time_fields = [
        ("time_bucket_key", True, False),
        ("bucket_name", False, False),
        ("min_minutes", False, False),
        ("max_minutes", False, False),
        ("sla_compliance_grade", False, False),
    ]
    draw_table_card(ax, 71, 14, 26, 20, "DIM_TIME_BUCKET (5 rows)", time_fields, "#d35400")

    # Draw Connecting Relationship Arrows (Dimensions -> Fact Table)
    arrows = [
        # dim_patient_cohort -> Fact
        ((29, 68), (35, 56), "1 : N (patient_cohort_key)"),
        # dim_activity -> Fact
        ((71, 72), (65, 56), "1 : N (activity_key)"),
        # dim_department -> Fact
        ((29, 24), (35, 38), "1 : N (department_key)"),
        # dim_time_bucket -> Fact
        ((71, 26), (65, 38), "1 : N (time_bucket_key)"),
    ]

    for (x1, y1), (x2, y2), label in arrows:
        ax.annotate(
            "", xy=(x2, y2), xytext=(x1, y1),
            arrowprops=dict(arrowstyle="-|>", color="#34495e", lw=2, mutation_scale=15, linestyle="-")
        )
        mid_x, mid_y = (x1 + x2) / 2, (y1 + y2) / 2
        ax.text(mid_x, mid_y + 1.2, label, ha="center", va="center",
                fontsize=7.5, fontweight="bold", color="#2c3e50",
                bbox=dict(boxstyle="round,pad=0.2", facecolor="#ecf0f1", edgecolor="none"))

    # Title Banner
    ax.text(50, 96, "CareFlow Clinical Pathway Dimensional Data Warehouse (Star-Schema Architecture)",
            ha="center", va="center", fontsize=13, fontweight="bold", color="#1a252f")
    ax.text(50, 93, "Optimized for Power BI / Executive Dashboard Slice-and-Dice Analytics | Author: Amit Prajapati (Member 3)",
            ha="center", va="center", fontsize=9, color="#7f8c8d")

    plt.tight_layout()
    chart_path = output_dir / "star_schema_entity_relationship.png"
    plt.savefig(chart_path, dpi=200, bbox_inches="tight")
    plt.close()
    print(f"Exported Star-Schema Architecture Diagram: {chart_path}")
    return chart_path

def main():
    print("Loading events for star-schema construction...")
    df = load_source_events()
    summary = build_star_schema(df)
    plot_star_schema_architecture()
    print("\nStar-Schema construction finished successfully.")

if __name__ == "__main__":
    main()
