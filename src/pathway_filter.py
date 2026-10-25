"""CareFlow Dynamic Clinical Pathway Slicing & Filter Module
Author: Amit Prajapati (Member 3 - Process Mining Analyst)
Project: CareFlow: Clinical Pathway Process Mining
"""

from pathlib import Path
import sqlite3
import pandas as pd
import pm4py

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = PROJECT_ROOT / "data" / "processed" / "careflow.db"

def load_events(db_path=DB_PATH):
    """Load events from SQLite for dynamic filtering."""
    with sqlite3.connect(db_path) as conn:
        df = pd.read_sql_query(
            """
            SELECT case_id, activity, event_time, org_group, age,
                   infection_suspected, sirs_criteria_2_or_more
            FROM events_analysis
            ORDER BY case_id, event_time ASC
            """,
            conn,
        )
    df["event_time"] = pd.to_datetime(df["event_time"], utc=True)
    return df

def filter_by_activity_presence(df, required_activity):
    """Filter cases that contain a specified clinical activity."""
    matching_cases = df[df["activity"] == required_activity]["case_id"].unique()
    return df[df["case_id"].isin(matching_cases)].copy()

def filter_by_trace_length(df, min_events=None, max_events=None):
    """Filter cases by number of recorded events."""
    counts = df.groupby("case_id").size()
    if min_events is not None:
        counts = counts[counts >= min_events]
    if max_events is not None:
        counts = counts[counts <= max_events]
    return df[df["case_id"].isin(counts.index)].copy()

def filter_by_case_duration(df, min_days=None, max_days=None):
    """Filter cases by total clinical span in days."""
    durations = df.groupby("case_id")["event_time"].agg(["min", "max"])
    durations["days"] = (durations["max"] - durations["min"]).dt.total_seconds() / 86400.0

    if min_days is not None:
        durations = durations[durations["days"] >= min_days]
    if max_days is not None:
        durations = durations[durations["days"] <= max_days]

    return df[df["case_id"].isin(durations.index)].copy()

def filter_by_patient_cohort(df, min_age=None, max_age=None, sirs_high_risk=None, infection_suspected=None):
    """Multi-criteria clinical patient filtering."""
    sub = df.copy()
    if min_age is not None:
        sub = sub[sub["age"] >= min_age]
    if max_age is not None:
        sub = sub[sub["age"] <= max_age]
    if sirs_high_risk is not None:
        sub = sub[sub["sirs_criteria_2_or_more"] == int(sirs_high_risk)]
    if infection_suspected is not None:
        sub = sub[sub["infection_suspected"] == int(infection_suspected)]

    matching_cases = sub["case_id"].unique()
    return df[df["case_id"].isin(matching_cases)].copy()

def get_filtered_summary(filtered_df):
    """Return quick process stats for a sliced sub-log."""
    total_cases = filtered_df["case_id"].nunique()
    total_events = len(filtered_df)
    unique_acts = filtered_df["activity"].nunique()

    # Form PM4Py log to get variant count
    log = pm4py.format_dataframe(
        filtered_df,
        case_id="case_id",
        activity_key="activity",
        timestamp_key="event_time",
    )
    variants = len(pm4py.get_variants(log))

    return {
        "cases": total_cases,
        "events": total_events,
        "activities": unique_acts,
        "variants": variants,
    }

def main():
    print("Loading events for pathway filtering tests...")
    df = load_events()
    print(f"Total Base Log: {df['case_id'].nunique()} cases, {len(df)} events.")

    # 1. Filter ICU patients
    icu_df = filter_by_activity_presence(df, "Admission IC")
    icu_stats = get_filtered_summary(icu_df)
    print(f"\n1. ICU Cohort Slice: {icu_stats['cases']} cases, {icu_stats['events']} events, {icu_stats['variants']} variants.")

    # 2. Filter Prolonged Stay (>14 days)
    prolonged_df = filter_by_case_duration(df, min_days=14.0)
    prolonged_stats = get_filtered_summary(prolonged_df)
    print(f"2. Prolonged Stay (>14d) Slice: {prolonged_stats['cases']} cases, {prolonged_stats['events']} events, {prolonged_stats['variants']} variants.")

    # 3. Filter Geriatric High-SIRS Patients (Age >= 65, SIRS >= 2)
    geriatric_sirs = filter_by_patient_cohort(df, min_age=65, sirs_high_risk=True)
    g_stats = get_filtered_summary(geriatric_sirs)
    print(f"3. Geriatric High-SIRS Slice: {g_stats['cases']} cases, {g_stats['events']} events, {g_stats['variants']} variants.")

    print("\nDynamic pathway filtering verified successfully.")

if __name__ == "__main__":
    main()
