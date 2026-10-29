
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt


# 1. Project paths
ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = ROOT / "data" / "raw" / "events.xlsx"
OUTPUT = ROOT / "reports" / "week3"
TRANSITIONS_OUTPUT = OUTPUT / "patient_transitions_regenerated.csv"

OUTPUT.mkdir(parents=True, exist_ok=True)


# 2. Normalize column names
def normalize_name(name):
    return (
        str(name)
        .strip()
        .lower()
        .replace(" ", "_")
        .replace("-", "_")
    )


# 3. Find a column using possible aliases
def find_column(columns, aliases):
    lookup = {normalize_name(column): column for column in columns}

    for alias in aliases:
        key = normalize_name(alias)
        if key in lookup:
            return lookup[key]

    return None


# 4. Main analysis
def main():
    # Check whether the dataset exists
    if not DATA_FILE.exists():
        raise FileNotFoundError(
            f"Dataset not found: {DATA_FILE}\n"
            "Please place events.xlsx inside data/raw/."
        )

    # Read Excel file
    df = pd.read_excel(DATA_FILE)

    print("Original shape:", df.shape)
    print("Columns:", df.columns.tolist())

    # Detect case/patient ID column
    case_col = find_column(
        df.columns,
        [
            "case:concept:name",
            "Case ID",
            "Case_ID",
            "caseid",
            "Patient ID",
            "patient_id",
            "case"
        ]
    )

    # Detect activity column
    activity_col = find_column(
        df.columns,
        [
            "concept:name",
            "Activity Name",
            "Activity_Name",
            "activity",
            "event_name",
            "event"
        ]
    )

    # Detect timestamp column
    timestamp_col = find_column(
        df.columns,
        [
            "time:timestamp",
            "Timestamp",
            "time_stamp",
            "datetime",
            "event_time",
            "event_timestamp"
        ]
    )

    print("\nDetected Case column:", case_col)
    print("Detected Activity column:", activity_col)
    print("Detected Timestamp column:", timestamp_col)

    # Stop if required columns are missing
    if not all([case_col, activity_col, timestamp_col]):
        raise ValueError(
            "Required columns not found.\n"
            f"Case column: {case_col}\n"
            f"Activity column: {activity_col}\n"
            f"Timestamp column: {timestamp_col}\n"
            "Check the dataset column names printed above."
        )

    # Rename selected columns to standard names
    df = df.rename(
        columns={
            case_col: "Case_ID",
            activity_col: "Activity_Name",
            timestamp_col: "Timestamp"
        }
    )

    # 5. Data cleaning
    df["Case_ID"] = df["Case_ID"].astype("string").str.strip()
    df["Activity_Name"] = (
        df["Activity_Name"].astype("string").str.strip()
    )

    df["Timestamp"] = pd.to_datetime(
        df["Timestamp"],
        errors="coerce",
        utc=True
    )

    rows_before = len(df)

    df = df.dropna(
        subset=["Case_ID", "Activity_Name", "Timestamp"]
    ).copy()

    df = df[
        (df["Case_ID"] != "")
        & (df["Activity_Name"] != "")
    ].copy()

    print("\nRows removed during cleaning:", rows_before - len(df))

    if df.empty:
        raise ValueError(
            "No valid event records remain after cleaning."
        )

    # 6. Sort events by patient and timestamp
    df = df.sort_values(
        ["Case_ID", "Timestamp"]
    ).reset_index(drop=True)

    # Save cleaned event log
    df.to_csv(
        OUTPUT / "cleaned_event_log.csv",
        index=False
    )

    # 7. Find each patient's next activity and timestamp
    grouped = df.groupby("Case_ID", sort=False)

    df["Next_Activity"] = grouped["Activity_Name"].shift(-1)
    df["Next_Timestamp"] = grouped["Timestamp"].shift(-1)

    df["Transition_Time_Minutes"] = (
        df["Next_Timestamp"] - df["Timestamp"]
    ).dt.total_seconds() / 60

    # Keep rows that have a next event
    transitions = df.dropna(
        subset=["Next_Activity", "Next_Timestamp"]
    ).copy()

    # Remove negative transition durations
    negative_count = (
        transitions["Transition_Time_Minutes"] < 0
    ).sum()

    print("Negative transitions removed:", negative_count)

    transitions = transitions[
        transitions["Transition_Time_Minutes"] >= 0
    ].copy()

    # Create activity transition labels
    transitions["Activity_Transition"] = (
        transitions["Activity_Name"].astype(str)
        + " -> "
        + transitions["Next_Activity"].astype(str)
    )

        # Save patient transitions to a new file
    transitions.to_csv(
        TRANSITIONS_OUTPUT,
        index=False
    )
    print("Patient transitions saved:", TRANSITIONS_OUTPUT)

    # 8. Calculate bottleneck summary
    if not transitions.empty:
        summary = (
            transitions.groupby(
                "Activity_Transition",
                as_index=False
            )
            .agg(
                Transition_Count=("Case_ID", "size"),
                Unique_Patients=("Case_ID", "nunique"),
                Average_Time_Minutes=(
                    "Transition_Time_Minutes", "mean"
                ),
                Median_Time_Minutes=(
                    "Transition_Time_Minutes", "median"
                ),
                Maximum_Time_Minutes=(
                    "Transition_Time_Minutes", "max"
                )
            )
            .sort_values(
                "Average_Time_Minutes",
                ascending=False
            )
            .reset_index(drop=True)
        )
    else:
        summary = pd.DataFrame(
            columns=[
                "Activity_Transition",
                "Transition_Count",
                "Unique_Patients",
                "Average_Time_Minutes",
                "Median_Time_Minutes",
                "Maximum_Time_Minutes"
            ]
        )

    summary.to_csv(
        OUTPUT / "bottleneck_summary.csv",
        index=False
    )

    # 9. Calculate dashboard KPIs
    average_transition = (
        transitions["Transition_Time_Minutes"].mean()
        if not transitions.empty else 0
    )

    longest_transition = (
        transitions["Transition_Time_Minutes"].max()
        if not transitions.empty else 0
    )

    kpis = pd.DataFrame([
        {
            "Metric": "Total Patients",
            "Value": df["Case_ID"].nunique()
        },
        {
            "Metric": "Total Events",
            "Value": len(df)
        },
        {
            "Metric": "Unique Activities",
            "Value": df["Activity_Name"].nunique()
        },
        {
            "Metric": "Total Transitions",
            "Value": len(transitions)
        },
        {
            "Metric": "Average Transition Time (Minutes)",
            "Value": average_transition
        },
        {
            "Metric": "Longest Transition Time (Minutes)",
            "Value": longest_transition
        }
    ])

    kpis.to_csv(
        OUTPUT / "week3_kpis.csv",
        index=False
    )

    # 10. Generate chart for the 10 slowest transitions
    chart_path = OUTPUT / "bottleneck_chart.png"

    if not summary.empty:
        top10 = (
            summary.head(10)
            .sort_values("Average_Time_Minutes")
        )

        plt.figure(figsize=(13, 7))

        plt.barh(
            top10["Activity_Transition"],
            top10["Average_Time_Minutes"]
        )

        plt.xlabel("Average Transition Time (Minutes)")
        plt.ylabel("Activity Transition")
        plt.title("Top 10 Hospital Process Bottlenecks")
        plt.tight_layout()

        plt.savefig(chart_path, dpi=150)
        plt.close()

        print("\nBottleneck chart saved:", chart_path)
    else:
        print("\nNo valid transitions available for the chart.")

    # 11. Display analysis results
    print("\n" + "=" * 60)
    print("TOP 10 BOTTLENECKS")
    print("=" * 60)

    if not summary.empty:
        print(summary.head(10).to_string(index=False))
    else:
        print("No bottlenecks found.")

    print("\n" + "=" * 60)
    print("KPI SUMMARY")
    print("=" * 60)
    print(kpis.to_string(index=False))

    print("\nAnalysis completed successfully.")
    print("Output folder:", OUTPUT)


if __name__ == "__main__":
    main()

