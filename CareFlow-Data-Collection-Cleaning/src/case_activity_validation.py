"""Validate case IDs and activity names in the local Sepsis Cases Event Log."""

from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATASET_FILENAME = "events.parquet"
CASE_ID_COLUMN = "case:concept:name"
ACTIVITY_COLUMN = "concept:name"
REQUIRED_COLUMNS = [CASE_ID_COLUMN, ACTIVITY_COLUMN]
TOP_ACTIVITY_LIMIT = 10


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
        print(f"Required column(s) missing from the dataset: {missing_columns}")
        print("Case and activity validation cannot continue.")
        raise SystemExit(1)

    case_ids = dataframe[CASE_ID_COLUMN]
    activity_names = dataframe[ACTIVITY_COLUMN]
    case_missing_count = int(case_ids.isna().sum())
    activity_missing_count = int(activity_names.isna().sum())
    case_empty_count = int(empty_or_whitespace_mask(case_ids).sum())
    activity_empty_count = int(empty_or_whitespace_mask(activity_names).sum())
    unique_case_ids = int(case_ids.nunique(dropna=True))
    unique_activity_names = int(activity_names.nunique(dropna=True))

    valid_activity_mask = (
        activity_names.notna() & ~empty_or_whitespace_mask(activity_names)
    )
    frequent_activities = (
        activity_names[valid_activity_mask]
        .value_counts()
        .head(TOP_ACTIVITY_LIMIT)
    )

    results = [
        {
            "Metric": "Dataset rows",
            "Column": "",
            "Value": len(dataframe),
            "Count": "",
        },
        {
            "Metric": "Missing values",
            "Column": CASE_ID_COLUMN,
            "Value": case_missing_count,
            "Count": "",
        },
        {
            "Metric": "Empty or whitespace-only strings",
            "Column": CASE_ID_COLUMN,
            "Value": case_empty_count,
            "Count": "",
        },
        {
            "Metric": "Unique non-missing values",
            "Column": CASE_ID_COLUMN,
            "Value": unique_case_ids,
            "Count": "",
        },
        {
            "Metric": "Missing values",
            "Column": ACTIVITY_COLUMN,
            "Value": activity_missing_count,
            "Count": "",
        },
        {
            "Metric": "Empty or whitespace-only strings",
            "Column": ACTIVITY_COLUMN,
            "Value": activity_empty_count,
            "Count": "",
        },
        {
            "Metric": "Unique non-missing values",
            "Column": ACTIVITY_COLUMN,
            "Value": unique_activity_names,
            "Count": "",
        },
    ]
    results.extend(
        {
            "Metric": "Most frequent activity",
            "Column": ACTIVITY_COLUMN,
            "Value": activity_name,
            "Count": int(count),
        }
        for activity_name, count in frequent_activities.items()
    )

    reports_directory = PROJECT_ROOT / "reports"
    reports_directory.mkdir(parents=True, exist_ok=True)
    csv_path = reports_directory / "day06_case_activity_validation.csv"
    markdown_path = reports_directory / "day06_case_activity_validation.md"

    pd.DataFrame(
        results, columns=["Metric", "Column", "Value", "Count"]
    ).to_csv(csv_path, index=False)

    report_lines = [
        "# Case and Activity Validation",
        "",
        "## Summary",
        "",
        f"- Dataset rows: {len(dataframe)}",
        f"- Unique non-missing case IDs: {unique_case_ids}",
        f"- Unique non-missing activity names: {unique_activity_names}",
        "",
        "## Findings",
        "",
        f"- `{CASE_ID_COLUMN}`: {case_missing_count} missing values and "
        f"{case_empty_count} empty or whitespace-only strings.",
        f"- `{ACTIVITY_COLUMN}`: {activity_missing_count} missing values and "
        f"{activity_empty_count} empty or whitespace-only strings.",
        "",
        f"Most frequent activity names (up to {TOP_ACTIVITY_LIMIT}; "
        "excluding missing and empty or whitespace-only values):",
        "",
    ]

    if frequent_activities.empty:
        report_lines.append("No non-empty activity names were found.")
    else:
        report_lines.extend(
            [
                "| Activity name | Count |",
                "| --- | ---: |",
            ]
        )
        report_lines.extend(
            f"| {activity_name} | {count} |"
            for activity_name, count in frequent_activities.items()
        )

    report_lines.extend(
        [
            "",
            "The original dataset was not modified.",
        ]
    )
    markdown_path.write_text("\n".join(report_lines) + "\n", encoding="utf-8")

    print(f"Read dataset: {dataset_path}")
    print(f"Dataset rows: {len(dataframe)}")
    print(f"{CASE_ID_COLUMN} missing values: {case_missing_count}")
    print(f"{CASE_ID_COLUMN} empty or whitespace-only strings: {case_empty_count}")
    print(f"Unique non-missing case IDs: {unique_case_ids}")
    print(f"{ACTIVITY_COLUMN} missing values: {activity_missing_count}")
    print(
        f"{ACTIVITY_COLUMN} empty or whitespace-only strings: {activity_empty_count}"
    )
    print(f"Unique non-missing activity names: {unique_activity_names}")
    print("Most frequent activity names:")
    for activity_name, count in frequent_activities.items():
        print(f"  {activity_name}: {count}")
    print(f"CSV report created: {csv_path}")
    print(f"Markdown report created: {markdown_path}")
    print("The original dataset was not modified.")


if __name__ == "__main__":
    main()
