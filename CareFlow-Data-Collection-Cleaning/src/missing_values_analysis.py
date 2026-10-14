"""Check missing values in the local Sepsis Cases Event Log."""

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

    row_count, column_count = dataframe.shape
    missing_counts = dataframe.isna().sum()
    if row_count > 0:
        missing_percentages = (missing_counts / row_count * 100).round(2)
    else:
        missing_percentages = missing_counts.astype(float)

    columns_with_missing_values = missing_counts[missing_counts > 0].index.tolist()
    results = pd.DataFrame(
        {
            "Column name": dataframe.columns,
            "Missing count": missing_counts.values,
            "Missing percentage": missing_percentages.values,
        }
    )

    reports_directory = PROJECT_ROOT / "reports"
    reports_directory.mkdir(parents=True, exist_ok=True)
    csv_path = reports_directory / "day03_missing_values_report.csv"
    markdown_path = reports_directory / "day03_missing_values_report.md"

    results.to_csv(csv_path, index=False)

    report_lines = [
        "# Missing Values Report",
        "",
        "## Summary",
        "",
        f"- Rows: {row_count}",
        f"- Columns: {column_count}",
        f"- Columns with missing values: {len(columns_with_missing_values)}",
        "",
        "## Findings",
        "",
    ]

    if columns_with_missing_values:
        report_lines.extend(
            [
                "| Column | Missing count | Missing percentage |",
                "| --- | ---: | ---: |",
            ]
        )
        for column_name in columns_with_missing_values:
            report_lines.append(
                f"| `{column_name}` | {missing_counts[column_name]} | "
                f"{missing_percentages[column_name]:.2f}% |"
            )
    else:
        report_lines.append("No columns have missing values.")

    markdown_path.write_text("\n".join(report_lines) + "\n", encoding="utf-8")

    print(f"Read dataset: {dataset_path}")
    print(f"Rows: {row_count}")
    print(f"Columns: {column_count}")
    print(f"Columns with missing values: {columns_with_missing_values}")
    print(f"CSV report created: {csv_path}")
    print(f"Markdown report created: {markdown_path}")


if __name__ == "__main__":
    main()
