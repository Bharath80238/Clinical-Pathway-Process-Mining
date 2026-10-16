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
    del modified_time  # Used to refresh the cache when the database changes.
    with sqlite3.connect(database_path) as connection:
        events = pd.read_sql_query(
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
    events["event_time"] = pd.to_datetime(
        events["event_time"],
        errors="coerce",
        utc=True,
    )
    events["case_id"] = events["case_id"].astype("string").str.strip()
    events["activity"] = events["activity"].astype("string").str.strip()
    events["org_group"] = (
        events["org_group"].astype("string").fillna("Unknown")
    )
    events.loc[events["org_group"].str.strip() == "", "org_group"] = "Unknown"
    for column in ["leucocytes", "crp", "lactic_acid"]:
        events[column] = pd.to_numeric(events[column], errors="coerce")
    return events
st.title("🏥 CareFlow")
st.subheader("Clinical Pathway Process Mining Dashboard")
st.markdown(
    """
    Explore clinical event records, activity patterns, pathway durations,
    intervals between events, and available clinical measurements.
    """
)
if not DB_PATH.exists():
    st.error(f"Database not found: {DB_PATH}")
    st.info(
        "Check that data/processed/careflow.db exists in your project folder."
    )
    st.stop()
try:
    events = load_events(
        str(DB_PATH),
        DB_PATH.stat().st_mtime,
    )
except Exception as error:
    st.error(f"Unable to load the database: {error}")
    st.info(
        "Confirm that the database contains an events_analysis table "
        "with the required columns."
    )
    st.stop()
if events.empty:
    st.warning("The events_analysis table contains no records.")
    st.stop()
required_columns = ["case_id", "activity", "event_time"]
valid_mask = (
    events["case_id"].notna()
    & events["case_id"].str.strip().ne("").fillna(False)
    & events["activity"].notna()
    & events["activity"].str.strip().ne("").fillna(False)
    & events["event_time"].notna()
)
valid_events = events.loc[valid_mask].copy()
if valid_events.empty:
    st.error("No valid events are available for analysis.")
    st.stop()
invalid_record_count = len(events) - len(valid_events)
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
    st.sidebar.warning("Start date is after end date.")
    st.stop()
start_timestamp = pd.Timestamp(start_date, tz="UTC")
end_timestamp = (
    pd.Timestamp(end_date, tz="UTC") + pd.Timedelta(days=1)
)
filtered = valid_events[
    (valid_events["event_time"] >= start_timestamp)
    & (valid_events["event_time"] < end_timestamp)
].copy()
activity_options = sorted(filtered["activity"].dropna().unique().tolist())
group_options = sorted(filtered["org_group"].dropna().unique().tolist())
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
filtered = filtered[
    filtered["activity"].isin(selected_activities)
    & filtered["org_group"].isin(selected_groups)
].copy()
if filtered.empty:
    st.warning("No records match the selected filters. Adjust the sidebar filters.")
    st.stop()
filtered = filtered.sort_values(
    ["case_id", "event_time"]
).reset_index(drop=True)
total_events = len(filtered)
unique_cases = filtered["case_id"].nunique()
unique_activities = filtered["activity"].nunique()
case_durations = (
    filtered.groupby("case_id")["event_time"]
    .agg(first_event="min", last_event="max")
    .reset_index()
)
case_durations["duration_hours"] = (
    case_durations["last_event"] - case_durations["first_event"]
).dt.total_seconds() / 3600
median_duration = case_durations["duration_hours"].median()
st.header("Key Performance Indicators")
kpi1, kpi2, kpi3, kpi4 = st.columns(4)
kpi1.metric("Total Events", f"{total_events:,}")
kpi2.metric("Unique Cases", f"{unique_cases:,}")
kpi3.metric("Unique Activities", f"{unique_activities:,}")
kpi4.metric(
    "Median Case Duration",
    f"{median_duration:,.2f} hours" if pd.notna(median_duration) else "N/A",
)
st.caption(
    "KPIs and charts reflect the selected date, activity, and organization-group filters."
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
    
def create_histogram(values, label_column, count_column, maximum_bins=10):
    """
    Convert numeric values into a chart-friendly DataFrame.

    String labels are used instead of Pandas Interval objects
    to avoid Altair category validation errors.
    """
    numeric_values = pd.to_numeric(
        pd.Series(values),
        errors="coerce",
    ).replace([np.inf, -np.inf], np.nan).dropna()

    if numeric_values.empty:
        return pd.DataFrame(columns=[label_column, count_column])
    number_of_bins = min(
        maximum_bins,
        max(1, numeric_values.nunique()),
    )
    counts, edges = np.histogram(
        numeric_values.to_numpy(dtype=float),
        bins=number_of_bins,
    )
    labels = [
        f"{edges[index]:,.2f} – {edges[index + 1]:,.2f}"
        for index in range(len(counts))
    ]
    return pd.DataFrame(
        {
            label_column: labels,
            count_column: counts,
        }
    )
st.header("Pathway Timing")
left, right = st.columns(2)
with left:
    st.subheader("Case Duration Distribution")
    st.caption(
        "Time between the first and last displayed event for each case, in hours."
    )
    duration_values = case_durations["duration_hours"].dropna()
    if not duration_values.empty:
        duration_counts = create_histogram(
            duration_values,
            label_column="Duration Range (hours)",
            count_column="Number of Cases",
        )
        st.bar_chart(
            duration_counts,
            x="Duration Range (hours)",
            y="Number of Cases",
        )
        st.metric(
            "Longest Displayed Case",
            f"{duration_values.max():,.2f} hours",
        )
    else:
        st.info("No valid case durations are available.")
with right:
    st.subheader("Intervals Between Displayed Events")
    st.caption(
        "Elapsed time between consecutive events within the same case, in minutes."
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
        interval_counts = create_histogram(
            intervals,
            label_column="Interval Range (minutes)",
            count_column="Number of Intervals",
        )
        st.bar_chart(
            interval_counts,
            x="Interval Range (minutes)",
            y="Number of Intervals",
        )
        st.metric(
            "Median Displayed Event Interval",
            f"{intervals.median():,.2f} minutes",
        )
    else:
        st.info(
            "At least two displayed events within a case are needed "
            "to calculate event intervals."
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
    measurement_data = filtered[
        ["case_id", "event_time", selected_measurement]
    ].dropna(subset=[selected_measurement])
    st.subheader(
        f"{selected_measurement.replace('_', ' ').title()} Distribution"
    )
    measurement_histogram = create_histogram(
        measurement_data[selected_measurement],
        label_column="Measurement Range",
        count_column="Number of Records",
    )
    st.bar_chart(
        measurement_histogram,
        x="Measurement Range",
        y="Number of Records",
    )
else:
    st.info("No usable clinical measurement values are available in this selection.")
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
    st.dataframe(
        missing_values,
        use_container_width=True,
        hide_index=True,
    )
with st.expander("Interpretation and limitations"):
    st.markdown(
        """
        - **Case duration:** calculated from the earliest and latest event
          visible for each case under the current filters. It may be shorter
          than the complete clinical journey.
        - **Event intervals:** calculated between consecutive displayed events
          within the same case, not between different cases.
        - **Filters:** changing the selected activities or organization groups
          can change the displayed duration and interval metrics.
        - **Clinical measurements:** descriptive statistics do not establish
          a diagnosis or prove that a measurement caused a delay.
        - **Process mining:** event sequences and repeated activities can
          identify patterns for further investigation, but do not by themselves
          prove a clinical bottleneck or poor care.
        - **Data quality:** invalid case IDs, activities, or timestamps are
          excluded from the pathway calculations and counted above.
        - **Dataset scope:** findings are limited to the records and fields
          available in the local database.
        """
    )
st.caption("CareFlow | Clinical Pathway Process Mining")