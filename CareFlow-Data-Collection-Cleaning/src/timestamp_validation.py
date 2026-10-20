"""Validate timestamps in the local Sepsis Cases Event Log."""

from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATASET_FILENAME = "events.parquet"
TIMESTAMP_COLUMN = "time:timestamp"


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

    if TIMESTAMP_COLUMN not in dataframe.columns:
        raise ValueError(f"Timestamp column {TIMESTAMP_COLUMN!r} was not found.")

    timestamps = dataframe[TIMESTAMP_COLUMN]
    missing_mask = timestamps.isna()
    parsed_timestamps = pd.to_datetime(timestamps, errors="coerce", utc=True)
    invalid_mask = ~missing_mask & parsed_timestamps.isna()
    valid_timestamps = parsed_timestamps[~missing_mask & parsed_timestamps.notna()]

    results = [
        ("Dataset rows", len(dataframe)),
        ("Timestamp column", TIMESTAMP_COLUMN),
        ("Missing timestamps", int(missing_mask.sum())),
        ("Invalid non-missing timestamps", int(invalid_mask.sum())),
        ("Valid timestamps", len(valid_timestamps)),
        (
            "Earliest valid timestamp",
            valid_timestamps.min().isoformat() if not valid_timestamps.empty else "",
        ),
        (
            "Latest valid timestamp",
            valid_timestamps.max().isoformat() if not valid_timestamps.empty else "",
        ),
    ]

    reports_directory = PROJECT_ROOT / "reports"
    reports_directory.mkdir(parents=True, exist_ok=True)
    csv_path = reports_directory / "day05_timestamp_validation_report.csv"
    markdown_path = reports_directory / "day05_timestamp_validation_report.md"

    pd.DataFrame(results, columns=["Metric", "Value"]).to_csv(csv_path, index=False)

    report_lines = [
        "# Timestamp Validation Report",
        "",
        "## Summary",
        "",
        f"- Dataset rows: {len(dataframe)}",
        f"- Timestamp column: `{TIMESTAMP_COLUMN}`",
        f"- Missing timestamps: {int(missing_mask.sum())}",
        f"- Invalid non-missing timestamps: {int(invalid_mask.sum())}",
        f"- Valid timestamps: {len(valid_timestamps)}",
        f"- Earliest valid timestamp: "
        f"{valid_timestamps.min().isoformat() if not valid_timestamps.empty else 'Not available'}",
        f"- Latest valid timestamp: "
        f"{valid_timestamps.max().isoformat() if not valid_timestamps.empty else 'Not available'}",
        "",
        "Missing and invalid timestamps are counted separately. The original dataset was not modified.",
    ]
    markdown_path.write_text("\n".join(report_lines) + "\n", encoding="utf-8")

    print(f"Read dataset: {dataset_path}")
    print(f"Timestamp column: {TIMESTAMP_COLUMN}")
    print(f"Missing timestamps: {int(missing_mask.sum())}")
    print(f"Invalid non-missing timestamps: {int(invalid_mask.sum())}")
    print(f"Valid timestamps: {len(valid_timestamps)}")
    print(f"Earliest valid timestamp: {results[5][1] or 'Not available'}")
    print(f"Latest valid timestamp: {results[6][1] or 'Not available'}")
    print(f"CSV report created: {csv_path}")
    print(f"Markdown report created: {markdown_path}")
    print("The original dataset was not modified.")


if __name__ == "__main__":
    main()
