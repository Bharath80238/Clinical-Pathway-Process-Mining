
from pathlib import Path
from io import BytesIO
import pandas as pd
import requests

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = PROJECT_ROOT / "data" / "raw"
EXCEL_PATH = RAW_DIR / "events.xlsx"
PARQUET_PATH = RAW_DIR / "events.parquet"
PARQUET_URL = (
    "https://huggingface.co/datasets/"
    "kondratevakate/sepsis-cases-event-log/"
    "resolve/main/events.parquet"
)
CASE_COL = "case:concept:name"
ACTIVITY_COL = "concept:name"
TIME_COL = "time:timestamp"

def load_source_parquet():
    """Download the source Parquet file for local comparison."""
    if PARQUET_PATH.exists():
        return pd.read_parquet(PARQUET_PATH)
    response = requests.get(PARQUET_URL, timeout=60)
    response.raise_for_status()

    PARQUET_PATH.write_bytes(response.content)
    return pd.read_parquet(BytesIO(response.content))
def summarize(name, df):
    print(f"\n--- {name} ---")
    print("Shape:", df.shape)
    print("Columns:", list(df.columns))
    print("Missing case IDs:", df[CASE_COL].isna().sum())
    print("Exact duplicate rows:", df.duplicated().sum())
    print("Unique non-missing cases:", df[CASE_COL].nunique())
    print("Unique activities:", df[ACTIVITY_COL].nunique())
    timestamps = pd.to_datetime(df[TIME_COL], errors="coerce", utc=True)
    print("Invalid/missing timestamps:", timestamps.isna().sum())
    print("Timestamp range:", timestamps.min(), "to", timestamps.max())

def main():
    if not EXCEL_PATH.exists():
        raise FileNotFoundError(
            f"Copy events.xlsx into this location first: {EXCEL_PATH}"
        )
    excel_df = pd.read_excel(EXCEL_PATH)
    source_df = load_source_parquet()
    for name, df in [("Excel copy", excel_df), ("Original Parquet", source_df)]:
        required = {CASE_COL, ACTIVITY_COL, TIME_COL}
        missing_columns = required - set(df.columns)
        if missing_columns:
            raise ValueError(
                f"{name} is missing required columns: {missing_columns}"
            )
        summarize(name, df)
    print("\n--- Comparison ---")
    print("Same row count:", len(excel_df) == len(source_df))
    print("Same column names:", set(excel_df.columns) == set(source_df.columns))
    if set(excel_df.columns) == set(source_df.columns):
        excel_aligned = excel_df[source_df.columns].copy()
        source_aligned = source_df.copy()
        for df in (excel_aligned, source_aligned):
            df[TIME_COL] = pd.to_datetime(
                df[TIME_COL], errors="coerce", utc=True
            )
        try:
            pd.testing.assert_frame_equal(
                excel_aligned.reset_index(drop=True),
                source_aligned.reset_index(drop=True),
                check_dtype=False,
                check_like=False,
            )
            print("Rows match in the same order after normalization.")
        except AssertionError as exc:
            print("Full comparison did not match.")
            print("Investigate formatting, ordering, and missing values.")
            print(str(exc)[:1500])

if __name__ == "__main__":
    main()
