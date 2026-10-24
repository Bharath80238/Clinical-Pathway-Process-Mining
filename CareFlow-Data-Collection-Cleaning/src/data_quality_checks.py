"""Run the main read-only data quality checks on the Sepsis Cases Event Log."""

from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATASET_FILENAME = "events.parquet"
CASE_ID_COLUMN = "case:concept:name"
ACTIVITY_COLUMN = "concept:name"
TIMESTAMP_COLUMN = "time:timestamp"
REQUIRED_COLUMNS = [CASE_ID_COLUMN, ACTIVITY_COLUMN, TIMESTAMP_COLUMN]


def find_dataset():
    """Look in the project folder, then in its containing workspace folder."""
    possible_paths = [
        PROJECT_ROOT / DATASET_FILENAME,
        PROJECT_ROOT.parent / DATASET_FILENAME,
    ]

    for path in possible_paths:
        if path.is_file():
            return path

    return None


def empty_or_whitespace_mask(series):
    """Identify empty or whitespace-only strings without changing values."""
    return series.map(
        lambda value: isinstance(value, str) and not value.strip()
    )


def main():
    dataset_path = find_dataset()
    if dataset_path is None:
        print(f"Could not find {DATASET_FILENAME}.")
        print(f"Place it in the project folder: {PROJECT_ROOT}")
        print(f"The containing workspace folder was also checked: {PROJECT_ROOT.parent}")
        raise SystemExit(1)

    try:
        dataframe = pd.read_parquet(dataset_path)
    except ImportError:
        print("A Parquet engine is missing. Install the required packages with:")
        print("python -m pip install pandas pyarrow")
        raise SystemExit(1)

    missing_columns = [
        column for column in REQUIRED_COLUMNS if column not in dataframe.columns
    ]
    if missing_columns:
        raise ValueError(f"Required column(s) missing from the dataset: {missing_columns}")

    row_count, column_count = dataframe.shape
    duplicate_count = int(dataframe.duplicated().sum())
    missing_counts = dataframe.isna().sum()
    missing_percentages = (
        missing_counts / row_count * 100 if row_count else missing_counts.astype(float)
    )

    empty_counts = {
        CASE_ID_COLUMN: int(empty_or_whitespace_mask(dataframe[CASE_ID_COLUMN]).sum()),
        ACTIVITY_COLUMN: int(empty_or_whitespace_mask(dataframe[ACTIVITY_COLUMN]).sum()),
    }

    timestamps = dataframe[TIMESTAMP_COLUMN]
    missing_timestamp_mask = timestamps.isna()
    parsed_timestamps = pd.to_datetime(timestamps, errors="coerce", utc=True)
    invalid_timestamp_mask = (
        ~missing_timestamp_mask & parsed_timestamps.isna()
    )
    valid_timestamps = parsed_timestamps[parsed_timestamps.notna()]
    earliest_timestamp = (
        valid_timestamps.min().isoformat() if not valid_timestamps.empty else ""
    )
    latest_timestamp = (
        valid_timestamps.max().isoformat() if not valid_timestamps.empty else ""
    )

    results = []
    for column_name in dataframe.columns:
        result = {
            "Column name": column_name,
            "Data type": str(dataframe[column_name].dtype),
            "Missing count": int(missing_counts[column_name]),
            "Missing percentage": round(float(missing_percentages[column_name]), 2),
            "Empty or whitespace-only count": "",
            "Invalid non-missing timestamp count": "",
            "Valid timestamp count": "",
            "Earliest valid timestamp": "",
            "Latest valid timestamp": "",
        }
        if column_name in empty_counts:
            result["Empty or whitespace-only count"] = empty_counts[column_name]
        if column_name == TIMESTAMP_COLUMN:
            result["Invalid non-missing timestamp count"] = int(
                invalid_timestamp_mask.sum()
            )
            result["Valid timestamp count"] = int(valid_timestamps.count())
            result["Earliest valid timestamp"] = earliest_timestamp
            result["Latest valid timestamp"] = latest_timestamp
        results.append(result)

    reports_directory = PROJECT_ROOT / "reports"
    reports_directory.mkdir(parents=True, exist_ok=True)
    csv_path = reports_directory / "day07_data_quality_report.csv"
    markdown_path = reports_directory / "day07_data_quality_report.md"

    pd.DataFrame(results).to_csv(csv_path, index=False)

    columns_with_missing_values = int((missing_counts > 0).sum())
    report_lines = [
        "# Data Quality Report",
        "",
        "## Summary",
        "",
        f"- Dataset: `{dataset_path}`",
        f"- Rows: {row_count}",
        f"- Columns: {column_count}",
        f"- Exact duplicate rows: {duplicate_count}",
        f"- Missing values: {int(missing_counts.sum())} across "
        f"{columns_with_missing_values} columns",
        "",
        "## Findings",
        "",
        f"- `{CASE_ID_COLUMN}`: {int(dataframe[CASE_ID_COLUMN].isna().sum())} "
        f"missing values and {empty_counts[CASE_ID_COLUMN]} empty or "
        "whitespace-only strings.",
        f"- `{ACTIVITY_COLUMN}`: {int(dataframe[ACTIVITY_COLUMN].isna().sum())} "
        f"missing values and {empty_counts[ACTIVITY_COLUMN]} empty or "
        "whitespace-only strings.",
        f"- `{TIMESTAMP_COLUMN}`: {int(missing_timestamp_mask.sum())} missing, "
        f"{int(invalid_timestamp_mask.sum())} invalid non-missing, and "
        f"{int(valid_timestamps.count())} valid timestamps.",
        f"- Earliest valid timestamp: {earliest_timestamp or 'Not available'}",
        f"- Latest valid timestamp: {latest_timestamp or 'Not available'}",
        "",
        "Per-column missing counts and applicable validation details are in the CSV report.",
        "The original dataset was not modified.",
    ]
    markdown_path.write_text("\n".join(report_lines) + "\n", encoding="utf-8")

    print(f"Read dataset: {dataset_path}")
    print(f"Rows: {row_count}")
    print(f"Columns: {column_count}")
    print(f"Exact duplicate rows: {duplicate_count}")
    print("\nMissing values by column:")
    print(missing_counts.to_string())
    for column_name in (CASE_ID_COLUMN, ACTIVITY_COLUMN):
        print(
            f"{column_name}: {int(dataframe[column_name].isna().sum())} missing, "
            f"{empty_counts[column_name]} empty or whitespace-only"
        )
    print(f"{TIMESTAMP_COLUMN} missing: {int(missing_timestamp_mask.sum())}")
    print(
        f"{TIMESTAMP_COLUMN} invalid non-missing: "
        f"{int(invalid_timestamp_mask.sum())}"
    )
    print(f"Earliest valid timestamp: {earliest_timestamp or 'Not available'}")
    print(f"Latest valid timestamp: {latest_timestamp or 'Not available'}")
    print(f"CSV report created: {csv_path}")
    print(f"Markdown report created: {markdown_path}")
    print("The original dataset was not modified.")


if __name__ == "__main__":
    main()
