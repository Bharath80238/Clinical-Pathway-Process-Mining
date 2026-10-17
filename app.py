import sqlite3
from pathlib import Path
import numpy as np
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="CareFlow | Clinical Pathway Analytics",
    page_icon="🏥",
    layout="wide",
)
PROJECT_DIR = Path(__file__).resolve().parent
DB_PATH = PROJECT_DIR / "data" / "processed" / "careflow.db"
@st.cache_data
def load_events(database_path, modified_time):
    del modified_time
    with sqlite3.connect(database_path) as connection:
        data = pd.read_sql_query(
            """
            SELECT
                case_id,
                activity,
                event_time,
                org_group,
                leucocytes,
                crp,
                lactic_acid
            FROM events_analysis
            """,
            connection,
        )

    data["event_time"] = pd.to_datetime(
        data["event_time"],
        errors="coerce",
        utc=True,
    )

    data["case_id"] = data["case_id"].astype("string").str.strip()
    data["activity"] = data["activity"].astype("string").str.strip()

    data["org_group"] = (
        data["org_group"].astype("string").fillna("Unknown")
    )
    data.loc[data["org_group"].str.strip() == "", "org_group"] = "Unknown"

    for column in ["leucocytes", "crp", "lactic_acid"]:
        data[column] = pd.to_numeric(data[column], errors="coerce")

    return data

st.title("🏥 CareFlow")
st.subheader("Clinical Pathway Process Mining Dashboard")

st.markdown(
    """
    Explore clinical event activity, case timelines, intervals between events,
    repeated activities, and available clinical measurements.
    """
)

if not DB_PATH.exists():
    st.error(f"Database not found: {DB_PATH}")
    st.info("Check that data/processed/careflow.db exists.")
    st.stop()

try:
    events = load_events(str(DB_PATH), DB_PATH.stat().st_mtime)
except Exception as error:
    st.error(f"Unable to load the database: {error}")
    st.stop()

if events.empty:
    st.warning("The events_analysis table contains no records.")
    st.stop()

valid_mask = (
    events["case_id"].notna()
    & events["case_id"].str.strip().ne("").fillna(False)
    & events["activity"].notna()
    & events["activity"].str.strip().ne("").fillna(False)
    & events["event_time"].notna()
)

valid_events = events.loc[valid_mask].copy()
invalid_record_count = len(events) - len(valid_events)

if valid_events.empty:
    st.error("No valid event records are available for analysis.")
    st.stop()

valid_events = valid_events.sort_values(
    ["case_id", "event_time"]
).reset_index(drop=True)

st.sidebar.header("Dashboard Filters")

minimum_date = valid_events["event_time"].min().date()
maximum_date = valid_events["event_time"].max().date()

selected_dates = st.sidebar.date_input(
    "Event date range",
    value=(minimum_date, maximum_date),
    min_value=minimum_date,
    max_value=maximum_date,
)

if isinstance(selected_dates, (tuple, list)):
    if len(selected_dates) == 2:
        start_date, end_date = selected_dates
    elif len(selected_dates) == 1:
        start_date = end_date = selected_dates[0]
    else:
        start_date, end_date = minimum_date, maximum_date
else:
    start_date = end_date = selected_dates

if start_date > end_date:
    st.sidebar.warning("Start date cannot be after end date.")
    st.stop()

start_timestamp = pd.Timestamp(start_date, tz="UTC")
end_timestamp = (
    pd.Timestamp(end_date, tz="UTC") + pd.Timedelta(days=1)
)

date_filtered = valid_events[
    (valid_events["event_time"] >= start_timestamp)
    & (valid_events["event_time"] < end_timestamp)
].copy()

activity_options = sorted(
    date_filtered["activity"].dropna().unique().tolist()
)
group_options = sorted(
    date_filtered["org_group"].dropna().unique().tolist()
)

selected_activities = st.sidebar.multiselect(
    "Activities",
    options=activity_options,
    default=activity_options,
)

selected_groups = st.sidebar.multiselect(
    "Organization groups",
    options=group_options,
    default=group_options,
)

filtered = date_filtered[
    date_filtered["activity"].isin(selected_activities)
    & date_filtered["org_group"].isin(selected_groups)
].copy()

if filtered.empty:
    st.warning("No records match the current filters. Adjust the sidebar.")
    st.stop()

filtered = filtered.sort_values(
    ["case_id", "event_time"]
).reset_index(drop=True)

full_case_durations = (
    valid_events.groupby("case_id")["event_time"]
    .agg(
        first_event="min",
        last_event="max",
    )
    .reset_index()
)

full_case_durations["duration_hours"] = (
    full_case_durations["last_event"]
    - full_case_durations["first_event"]
).dt.total_seconds() / 3600

full_case_median = full_case_durations["duration_hours"].median()

filtered_case_durations = (
    filtered.groupby("case_id")["event_time"]
    .agg(
        first_event="min",
        last_event="max",
    )
    .reset_index()
)

filtered_case_durations["duration_hours"] = (
    filtered_case_durations["last_event"]
    - filtered_case_durations["first_event"]
).dt.total_seconds() / 3600

filtered_case_median = (
    filtered_case_durations["duration_hours"].median()
)

total_events = len(filtered)
unique_cases = filtered["case_id"].nunique()
unique_activities = filtered["activity"].nunique()

st.header("Key Performance Indicators")

kpi1, kpi2, kpi3, kpi4 = st.columns(4)

kpi1.metric("Filtered Events", f"{total_events:,}")
kpi2.metric("Cases in Filtered Events", f"{unique_cases:,}")
kpi3.metric("Filtered Activities", f"{unique_activities:,}")
kpi4.metric(
    "Full-Case Median Duration",
    f"{full_case_median:,.2f} hours"
    if pd.notna(full_case_median)
    else "N/A",
)

st.caption(
    "Full-case duration uses all valid database events. "
    "The other event and activity KPIs reflect the selected filters."
)

st.subheader("Case Duration Comparison")

duration_col1, duration_col2 = st.columns(2)

with duration_col1:
    st.metric(
        "Full-Case Median Duration",
        f"{full_case_median:,.2f} hours"
        if pd.notna(full_case_median)
        else "N/A",
        help=(
            "Calculated from the first and last valid event for each case "
            "across the complete dataset."
        ),
    )

with duration_col2:
    st.metric(
        "Filtered-Event Median Duration",
        f"{filtered_case_median:,.2f} hours"
        if pd.notna(filtered_case_median)
        else "N/A",
        help=(
            "Calculated from the first and last events remaining for each "
            "case after all selected filters."
        ),
    )

st.header("Activity Analysis")

left, right = st.columns(2)

with left:
    st.subheader("Most Frequent Activities")

    activity_counts = (
        filtered["activity"]
        .value_counts()
        .head(15)
        .sort_values()
        .rename_axis("Activity")
        .reset_index(name="Number of Events")
    )

    st.bar_chart(
        activity_counts,
        x="Activity",
        y="Number of Events",
    )

with right:
    st.subheader("Cases with the Most Events")

    events_per_case = (
        filtered.groupby("case_id")
        .size()
        .sort_values(ascending=False)
        .head(20)
        .sort_values()
        .rename_axis("Case ID")
        .reset_index(name="Number of Events")
    )

    st.bar_chart(
        events_per_case,
        x="Case ID",
        y="Number of Events",
    )

def make_histogram(values, bin_edges, label_column, count_column):
    """Build chart-ready histogram data with string category labels."""

    numeric_values = pd.to_numeric(
        pd.Series(values),
        errors="coerce",
    ).replace([np.inf, -np.inf], np.nan).dropna()

    counts, edges = np.histogram(
        numeric_values.to_numpy(dtype=float),
        bins=bin_edges,
    )

    labels = [
        f"{edges[i]:,.2f} – {edges[i + 1]:,.2f}"
        for i in range(len(counts))
    ]

    return pd.DataFrame(
        {
            label_column: labels,
            count_column: counts,
        }
    )


def shared_bin_edges(first_values, second_values, maximum_bins=10):
    """Create shared bin edges so two histograms are comparable."""

    first = pd.to_numeric(
        pd.Series(first_values), errors="coerce"
    ).replace([np.inf, -np.inf], np.nan).dropna()

    second = pd.to_numeric(
        pd.Series(second_values), errors="coerce"
    ).replace([np.inf, -np.inf], np.nan).dropna()

    combined = pd.concat([first, second], ignore_index=True)

    if combined.empty:
        return None

    minimum = float(combined.min())
    maximum = float(combined.max())

    if minimum == maximum:
        padding = max(abs(minimum) * 0.01, 0.5)
        minimum -= padding
        maximum += padding

    number_of_bins = min(
        maximum_bins,
        max(1, int(combined.nunique())),
    )

    return np.linspace(minimum, maximum, number_of_bins + 1)

st.header("Pathway Timing")

left, right = st.columns(2)

with left:
    st.subheader("Full vs Filtered Case Duration")

    st.caption(
        "Both distributions use the same duration-bin boundaries. "
        "Duration is the span between the first and last displayed event "
        "for each case."
    )

    full_values = full_case_durations["duration_hours"].dropna()
    filtered_values = filtered_case_durations["duration_hours"].dropna()

    edges = shared_bin_edges(full_values, filtered_values)

    if edges is not None:
        full_histogram = make_histogram(
            full_values,
            edges,
            label_column="Duration Range (hours)",
            count_column="Full Cases",
        )

        filtered_histogram = make_histogram(
            filtered_values,
            edges,
            label_column="Duration Range (hours)",
            count_column="Filtered Cases",
        )

        duration_comparison = full_histogram.merge(
            filtered_histogram,
            on="Duration Range (hours)",
            how="outer",
        ).fillna(0)

        duration_comparison = duration_comparison.set_index(
            "Duration Range (hours)"
        )

        st.bar_chart(duration_comparison)

        with st.expander("View duration statistics"):
            st.write("Full-case duration (hours)")
            st.dataframe(
                full_values.describe().round(2).to_frame().T,
                use_container_width=True,
            )

            st.write("Filtered-event duration (hours)")
            st.dataframe(
                filtered_values.describe().round(2).to_frame().T,
                use_container_width=True,
            )
    else:
        st.info("No case durations are available.")

with right:
    st.subheader("Intervals Between Displayed Events")

    st.caption(
        "Elapsed time between consecutive displayed events within the same case."
    )

    filtered["previous_event_time"] = (
        filtered.groupby("case_id")["event_time"].shift(1)
    )

    filtered["interval_minutes"] = (
        filtered["event_time"] - filtered["previous_event_time"]
    ).dt.total_seconds() / 60

    intervals = (
        filtered["interval_minutes"]
        .replace([np.inf, -np.inf], np.nan)
        .dropna()
    )

    if not intervals.empty:
        interval_edges = shared_bin_edges(intervals, intervals)

        interval_histogram = make_histogram(
            intervals,
            interval_edges,
            label_column="Interval Range (minutes)",
            count_column="Number of Intervals",
        )

        st.bar_chart(
            interval_histogram,
            x="Interval Range (minutes)",
            y="Number of Intervals",
        )

        st.metric(
            "Median Displayed Event Interval",
            f"{intervals.median():,.2f} minutes",
        )
    else:
        st.info(
            "At least two displayed events within the same case are required "
            "to calculate an interval."
        )

st.header("Repeated Activity Analysis")

repeated_activities = (
    filtered.groupby(["case_id", "activity"])
    .size()
    .reset_index(name="Occurrences")
)

repeated_activities = repeated_activities[
    repeated_activities["Occurrences"] > 1
]

if not repeated_activities.empty:
    repeated_summary = (
        repeated_activities.groupby("activity")
        .agg(
            Cases_with_Repeats=("case_id", "nunique"),
            Total_Repeated_Occurrences=("Occurrences", "sum"),
        )
        .sort_values("Cases_with_Repeats", ascending=False)
        .head(15)
        .reset_index()
        .rename(columns={"activity": "Activity"})
    )

    st.bar_chart(
        repeated_summary,
        x="Activity",
        y="Cases_with_Repeats",
    )

    with st.expander("View repeated activity details"):
        st.dataframe(
            repeated_summary,
            use_container_width=True,
            hide_index=True,
        )
else:
    st.info("No repeated activities were found for the selected filters.")

st.header("Clinical Measurement Overview")

measurement_columns = [
    "leucocytes",
    "crp",
    "lactic_acid",
]

available_measurements = [
    column
    for column in measurement_columns
    if column in filtered.columns
    and filtered[column].notna().any()
]

if available_measurements:
    measurement_summary = (
        filtered[available_measurements]
        .describe()
        .T
        .rename_axis("Measurement")
        .reset_index()
        .round(2)
    )

    st.dataframe(
        measurement_summary,
        use_container_width=True,
        hide_index=True,
    )

    selected_measurement = st.selectbox(
        "Select a measurement to explore",
        options=available_measurements,
        format_func=lambda name: name.replace("_", " ").title(),
    )

    measurement_data = filtered[selected_measurement].dropna()

    measurement_edges = shared_bin_edges(
        measurement_data,
        measurement_data,
    )

    if measurement_edges is not None:
        measurement_histogram = make_histogram(
            measurement_data,
            measurement_edges,
            label_column="Measurement Range",
            count_column="Number of Records",
        )

        st.bar_chart(
            measurement_histogram,
            x="Measurement Range",
            y="Number of Records",
        )
else:
    st.info(
        "No usable clinical measurement values are available "
        "for the current filters."
    )

st.header("Filtered Event Records")

st.write(f"Displaying **{len(filtered):,}** event records.")

display_columns = [
    "case_id",
    "activity",
    "event_time",
    "org_group",
    "leucocytes",
    "crp",
    "lactic_acid",
]

display_columns = [
    column for column in display_columns if column in filtered.columns
]

st.dataframe(
    filtered[display_columns],
    use_container_width=True,
    hide_index=True,
)

csv_data = filtered[display_columns].copy()
csv_data["event_time"] = csv_data["event_time"].astype(str)

st.download_button(
    label="Download Filtered Events as CSV",
    data=csv_data.to_csv(index=False).encode("utf-8"),
    file_name="careflow_filtered_events.csv",
    mime="text/csv",
)
st.header("Data Quality Summary")

quality1, quality2, quality3 = st.columns(3)

quality1.metric("Source Records", f"{len(events):,}")
quality2.metric("Valid Event Records", f"{len(valid_events):,}")
quality3.metric("Excluded Invalid Records", f"{invalid_record_count:,}")

with st.expander("View missing values"):
    missing_values = (
        events.isna()
        .sum()
        .rename_axis("Column")
        .reset_index(name="Missing Values")
    )

    missing_values["Missing Percentage"] = (
        missing_values["Missing Values"] / len(events) * 100
    ).round(2)

    st.dataframe(
        missing_values,
        use_container_width=True,
        hide_index=True,
    )

with st.expander("Interpretation and limitations"):
    st.markdown(
        """
        - **Full-case duration:** calculated from the earliest and latest valid
          event for each case in the complete dataset.
        - **Filtered-event duration:** calculated from the earliest and latest
          event remaining for each case after the selected filters.
        - **Date filters:** full-case duration remains based on the entire
          dataset; filtered-event duration changes with the selected date range.
        - **Intervals:** calculated between consecutive displayed events within
          the same case. Filtering can remove intermediate events, so these
          intervals may span events that were not displayed.
        - **Clinical measurements:** descriptive statistics do not establish a
          diagnosis or prove that a measurement caused a delay.
        - **Data quality:** invalid case IDs, activities, or timestamps are
          excluded from pathway calculations and counted above.
        - **Process mining:** repeated activities and long intervals identify
          patterns for investigation but do not independently prove a bottleneck.
        """
    )
st.caption("CareFlow | Clinical Pathway Process Mining")