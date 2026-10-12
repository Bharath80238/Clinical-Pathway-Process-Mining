"""Print a read-only overview of the local Sepsis Cases Event Log."""

from pathlib import Path

try:
    import pandas as pd
except ImportError:
    print("pandas is missing. Install the required packages with:")
    print("python -m pip install pandas pyarrow")
    raise SystemExit(1)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATASET_FILENAME = "events.parquet"
IMPORTANT_FIELDS = [
    "case:concept:name",
    "concept:name",
    "time:timestamp",
]


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
        print(f"Place it in the project root: {PROJECT_ROOT}")
        print(f"The containing workspace was also checked: {PROJECT_ROOT.parent}")
        return

    try:
        dataframe = pd.read_parquet(dataset_path)
    except ImportError:
        print("A Parquet engine is missing. Install the required packages with:")
        print("python -m pip install pandas pyarrow")
        return

    print(f"Dataset file: {dataset_path}")
    print(f"Rows: {dataframe.shape[0]}")
    print(f"Columns: {dataframe.shape[1]}")

    print("\n--- COLUMN NAMES AND DATA TYPES ---")
    for column_name, data_type in dataframe.dtypes.items():
        print(f"{column_name}: {data_type}")

    print("\n--- FIRST FIVE RECORDS ---")
    print(dataframe.head().to_string(index=False))

    print("\n--- MISSING VALUES BY COLUMN ---")
    print(dataframe.isna().sum().to_string())

    print("\n--- EXACT DUPLICATE ROWS ---")
    print(int(dataframe.duplicated().sum()))

    print("\n--- IMPORTANT EVENT-LOG FIELD TYPES ---")
    for field_name in IMPORTANT_FIELDS:
        if field_name in dataframe.columns:
            print(f"{field_name}: {dataframe[field_name].dtype}")
        else:
            print(f"{field_name}: not present")

    print("\nThe dataset was not modified.")


if __name__ == "__main__":
    main()
