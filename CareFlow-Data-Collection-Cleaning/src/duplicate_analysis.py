"""Check exact duplicate rows in the local Sepsis Cases Event Log."""

from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATASET_FILENAME = "events.parquet"


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

    total_rows = len(dataframe)
    duplicate_mask = dataframe.duplicated()
    duplicate_count = int(duplicate_mask.sum())
    duplicate_percentage = (
        duplicate_count / total_rows * 100 if total_rows else 0.0
    )

    reports_directory = PROJECT_ROOT / "reports"
    reports_directory.mkdir(parents=True, exist_ok=True)
    markdown_path = reports_directory / "day04_duplicate_analysis_report.md"
    csv_path = reports_directory / "day04_duplicate_rows.csv"

    report_lines = [
        "# Duplicate Records Report",
        "",
        "## Summary",
        "",
        f"- Total rows: {total_rows}",
        f"- Exact duplicate rows: {duplicate_count}",
        f"- Duplicate percentage: {duplicate_percentage:.2f}%",
        "",
        "## Findings",
        "",
    ]

    if duplicate_count:
        dataframe.loc[duplicate_mask].to_csv(csv_path, index=False)
        report_lines.append(
            f"Found {duplicate_count} exact duplicate rows. "
            "Repeated occurrences after the first copy are included in the CSV."
        )
    else:
        report_lines.append("No exact duplicate rows were found.")

    markdown_path.write_text("\n".join(report_lines) + "\n", encoding="utf-8")

    print(f"Read dataset: {dataset_path}")
    print(f"Total rows: {total_rows}")
    print(f"Exact duplicate rows: {duplicate_count}")
    print(f"Duplicate percentage: {duplicate_percentage:.2f}%")
    if duplicate_count:
        print(f"Duplicate rows CSV created: {csv_path}")
    print(f"Markdown report created: {markdown_path}")
    print("The original dataset was not modified.")


if __name__ == "__main__":
    main()
