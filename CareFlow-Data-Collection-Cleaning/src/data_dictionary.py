"""Create a data dictionary from the local Sepsis Cases Event Log."""

import csv
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATASET_FILENAME = "events.parquet"
COLUMN_DESCRIPTIONS = {
    "case:concept:name": "Case identifier",
    "concept:name": "Activity name",
    "time:timestamp": "Event timestamp",
}


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

    data_directory = PROJECT_ROOT / "data"
    csv_path = data_directory / "data_dictionary.csv"
    markdown_path = data_directory / "data_dictionary.md"

    with csv_path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(["Column name", "Data type"])
        for column_name, data_type in dataframe.dtypes.items():
            writer.writerow([column_name, str(data_type)])

    markdown_lines = [
        "# Data Dictionary",
        "",
        "The Sepsis Cases Event Log records event data for cases. This dictionary "
        "lists column names and data types observed by reading the local "
        "`events.parquet` file with pandas. Meanings not supported by the existing "
        "project documentation are marked `To be verified`.",
        "",
        "| Column name | Data type | Description |",
        "| --- | --- | --- |",
    ]
    for column_name, data_type in dataframe.dtypes.items():
        description = COLUMN_DESCRIPTIONS.get(column_name, "To be verified")
        markdown_lines.append(
            f"| `{column_name}` | `{data_type}` | {description} |"
        )

    markdown_path.write_text("\n".join(markdown_lines) + "\n", encoding="utf-8")

    print(f"Read dataset: {dataset_path}")
    print(f"Rows: {len(dataframe)}")
    print(f"Columns included: {len(dataframe.columns)}")
    print(f"CSV created: {csv_path}")
    print(f"Markdown created: {markdown_path}")


if __name__ == "__main__":
    main()
