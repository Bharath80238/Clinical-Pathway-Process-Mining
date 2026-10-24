"""CareFlow Organizational Resource Mining & Departmental Analysis
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

# Functional mapping of organizational groups to clinical hospital departments
DEPARTMENT_MAPPING = {
    "A": "Emergency Clinical Staff (Team A)",
    "B": "Central Diagnostic Laboratory",
    "C": "Emergency Triage Assessment Unit",
    "E": "Discharge & Outpatient Administration",
    "?": "Emergency Readmission (Unplanned)",
    "L": "Emergency Clinical Staff (Team B)",
    "P": "Intensive Care Unit (ICU Team P)",
    "W": "Intensive Care Unit (ICU Team W)",
    "J": "Intensive Care Unit (ICU Team J)",
    "K": "Intensive Care Unit (ICU Team K)",
}

def get_department_label(code):
    """Resolve org:group code into a standardized clinical department name."""
    if pd.isna(code) or str(code).strip() == "":
        return "Unassigned / Unknown"
    code = str(code).strip()
    if code in DEPARTMENT_MAPPING:
        return DEPARTMENT_MAPPING[code]
    # Wards (F, G, H, I, M, N, O, Q, R, S, T, U, V, X, Y)
    return f"General Inpatient Ward ({code})"

def load_org_events(db_path=DB_PATH):
    """Load events joined with clinical departmental metadata."""
    if not Path(db_path).exists():
        raise FileNotFoundError(f"Database not found at: {db_path}")

    with sqlite3.connect(db_path) as conn:
        df = pd.read_sql_query(
            """
            SELECT case_id, activity, event_time, org_group
            FROM events_analysis
            ORDER BY case_id, event_time ASC
            """,
            conn,
        )

    df["event_time"] = pd.to_datetime(df["event_time"], utc=True)
    df["org_group"] = df["org_group"].fillna("Unassigned").astype(str).str.strip()
    df["department"] = df["org_group"].apply(get_department_label)
    return df

def compute_department_profiles(df):
    """Compute workload, case involvement, and activity distribution across departments."""
    total_events = len(df)
    total_cases = df["case_id"].nunique()

    profiles = []
    for (code, dept), group in df.groupby(["org_group", "department"]):
        events_cnt = len(group)
        cases_cnt = group["case_id"].nunique()
        acts = sorted(group["activity"].unique())
        
        profiles.append({
            "org_code": code,
            "department": dept,
            "total_events": events_cnt,
            "event_share_pct": round((events_cnt / total_events) * 100, 2),
            "patient_cases_involved": cases_cnt,
            "patient_reach_pct": round((cases_cnt / total_cases) * 100, 2),
            "unique_activity_count": len(acts),
            "activities_handled": ", ".join(acts),
            "avg_events_per_patient": round(events_cnt / cases_cnt, 2),
        })

    profile_df = pd.DataFrame(profiles).sort_values("total_events", ascending=False).reset_index(drop=True)
    return profile_df

def compute_handoff_matrix(df):
    """Compute organizational handoff transitions (handover of work network)."""
    df_sorted = df.copy()
    df_sorted["next_dept"] = df_sorted.groupby("case_id")["department"].shift(-1)
    df_sorted["next_org_code"] = df_sorted.groupby("case_id")["org_group"].shift(-1)

    handoffs = df_sorted.dropna(subset=["next_dept", "next_org_code"]).copy()

    handoff_matrix = handoffs.groupby(
        ["org_group", "department", "next_org_code", "next_dept"]
    ).size().reset_index(name="handoff_count")

    handoff_matrix = handoff_matrix.sort_values("handoff_count", ascending=False).reset_index(drop=True)
    
    # Export CSVs
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    handoff_matrix.to_csv(REPORTS_DIR / "org_handoff_matrix.csv", index=False)
    print(f"Exported handoff matrix: {REPORTS_DIR / 'org_handoff_matrix.csv'}")
    return handoff_matrix

def plot_org_workload(profile_df, top_n=10):
    """Plot workload distribution across hospital departments."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    subset = profile_df.head(top_n).sort_values("total_events", ascending=True)

    plt.figure(figsize=(12, 6))
    bars = plt.barh(subset["department"], subset["total_events"], color="#16a085", edgecolor="black", alpha=0.85)

    plt.title(f"Top {top_n} Hospital Departments by Event Volume & Workload", fontsize=12, fontweight="bold")
    plt.xlabel("Total Recorded Events", fontsize=10, fontweight="bold")
    plt.ylabel("Clinical Department / Unit", fontsize=10, fontweight="bold")

    for bar in bars:
        w = bar.get_width()
        pct = (w / profile_df["total_events"].sum()) * 100
        plt.annotate(
            f"{int(w):,} ({pct:.1f}%)",
            xy=(w, bar.get_y() + bar.get_height() / 2),
            xytext=(5, 0),
            textcoords="offset points",
            ha="left",
            va="center",
            fontsize=9,
            fontweight="bold",
        )

    plt.tight_layout()
    chart_path = OUTPUT_DIR / "org_workload_distribution.png"
    plt.savefig(chart_path, dpi=200)
    plt.close()
    print(f"Created workload chart: {chart_path}")

def plot_org_handoff_heatmap(handoff_df, top_n=6):
    """Plot cross-departmental patient handoff transfer matrix."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    top_orgs = (
        handoff_df.groupby("org_group")["handoff_count"].sum().nlargest(top_n).index.tolist()
    )

    # Filter matrix to top units
    sub = handoff_df[
        (handoff_df["org_group"].isin(top_orgs)) & (handoff_df["next_org_code"].isin(top_orgs))
    ].copy()

    pivot = sub.pivot_table(
        index="org_group",
        columns="next_org_code",
        values="handoff_count",
        fill_value=0,
    )

    labels = [DEPARTMENT_MAPPING.get(c, c) for c in pivot.index]

    plt.figure(figsize=(9, 7))
    plt.imshow(pivot.values, cmap="YlOrRd", aspect="auto")
    plt.colorbar(label="Patient Transfers / Handoff Count")

    plt.xticks(range(len(pivot.columns)), pivot.columns, fontsize=10, fontweight="bold")
    plt.yticks(range(len(pivot.index)), [f"{c}: {l[:22]}" for c, l in zip(pivot.index, labels)], fontsize=9)

    plt.title("Cross-Department Patient Care Handoff Matrix", fontsize=12, fontweight="bold", pad=12)
    plt.xlabel("Receiving Department Code (org:group)", fontsize=10, fontweight="bold")
    plt.ylabel("Transferring Department Code", fontsize=10, fontweight="bold")

    for i in range(len(pivot.index)):
        for j in range(len(pivot.columns)):
            val = int(pivot.values[i, j])
            if val > 0:
                color = "white" if val > pivot.values.max() / 2 else "black"
                plt.text(j, i, f"{val:,}", ha="center", va="center", color=color, fontsize=8.5, fontweight="bold")

    plt.tight_layout()
    chart_path = OUTPUT_DIR / "org_handoff_heatmap.png"
    plt.savefig(chart_path, dpi=200)
    plt.close()
    print(f"Created handoff heatmap: {chart_path}")

def main():
    print("Loading organizational events...")
    df = load_org_events()
    print(f"Loaded {len(df)} events with {df['org_group'].nunique()} organizational groups.")
    
    print("\nComputing department workload profiles...")
    profile_df = compute_department_profiles(df)
    profile_df.to_csv(REPORTS_DIR / "org_department_profiles.csv", index=False)
    print(f"Exported department profiles: {REPORTS_DIR / 'org_department_profiles.csv'}")

    print("\nComputing organizational handoff matrix...")
    handoff_df = compute_handoff_matrix(df)

    print("\nGenerating organizational charts...")
    plot_org_workload(profile_df)
    plot_org_handoff_heatmap(handoff_df)
    print("\nOrganizational resource mining completed successfully.")

if __name__ == "__main__":
    main()
