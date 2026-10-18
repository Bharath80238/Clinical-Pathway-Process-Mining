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
BOOLEAN_COLUMNS = [
    "InfectionSuspected",
    "DiagnosticBlood",
    "DisfuncOrg",
    "SIRSCritTachypnea",
    "Hypotensie",
    "SIRSCritHeartRate",
    "Infusion",
    "DiagnosticArtAstrup",
    "DiagnosticIC",
    "DiagnosticSputum",
    "DiagnosticLiquor",
    "DiagnosticOther",
    "SIRSCriteria2OrMore",
    "DiagnosticXthorax",
    "SIRSCritTemperature",
    "DiagnosticUrinaryCulture",
    "SIRSCritLeucos",
    "Oligurie",
    "DiagnosticLacticAcid",
    "Hypoxie",
    "DiagnosticUrinarySediment",
    "DiagnosticECG",
]
def load_source_parquet():
    """Load the local Parquet file or download it if absent."""
    if PARQUET_PATH.exists():
        return pd.read_parquet(PARQUET_PATH)
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    response = requests.get(PARQUET_URL, timeout=60)
    response.raise_for_status()
    PARQUET_PATH.write_bytes(response.content)
    return pd.read_parquet(BytesIO(response.content))

def summarize(name, df):
    """Print a basic summary of a dataset."""
    print(f"\n--- {name} ---")
    print("Shape:", df.shape)
    print("Columns:", list(df.columns))
    print("Missing case IDs:", int(df[CASE_COL].isna().sum()))
    print("Exact duplicate rows:", int(df.duplicated().sum()))
    print("Unique non-missing cases:", df[CASE_COL].nunique())
    print("Unique activities:", df[ACTIVITY_COL].nunique())
    timestamps = pd.to_datetime(
        df[TIME_COL],
        errors="coerce",
        utc=True,
    )
    print("Invalid/missing timestamps:", int(timestamps.isna().sum()))
    print("Timestamp range:", timestamps.min(), "to", timestamps.max())
def normalize_boolean(value):
    """Make Boolean and numeric 0/1 values comparable."""
    if pd.isna(value):
        return "<MISSING>"

    if isinstance(value, (bool,)):
        return "TRUE" if value else "FALSE"

    if isinstance(value, (int, float)) and value in (0, 1):
        return "TRUE" if value == 1 else "FALSE"

    text = str(value).strip().upper()

    if text in {"TRUE", "FALSE"}:
        return text

    return text


def normalize_frame(df):
    """Normalize representation differences without changing literal 'NA'."""
    result = df.copy()

    for col in BOOLEAN_COLUMNS:
        if col in result.columns:
            result[col] = result[col].map(normalize_boolean)

    # Normalize timestamps to the same UTC string representation.
    result[TIME_COL] = (
        pd.to_datetime(result[TIME_COL], errors="coerce", utc=True)
        .astype("string")
        .fillna("<MISSING>")
    )

    for col in result.columns:
        if col == TIME_COL or col in BOOLEAN_COLUMNS:
            continue

        if pd.api.types.is_numeric_dtype(result[col]):
            # Standardize numeric columns and their missing values.
            result[col] = pd.to_numeric(result[col], errors="coerce")
        else:
            # Normalize actual missing values, but preserve literal "NA".
            result[col] = result[col].map(
                lambda value: (
                    "<MISSING>" if pd.isna(value) else str(value)
                )
            )

    return result


def compare_datasets(excel_df, parquet_df):
    """Compare both datasets after representation normalization."""
    print("\n--- Comparison ---")

    same_rows = len(excel_df) == len(parquet_df)
    same_columns = list(excel_df.columns) == list(parquet_df.columns)

    print("Same row count:", same_rows)
    print("Same column names and order:", same_columns)

    if not same_rows:
        print("FAIL: Row counts differ.")
        return False

    if not same_columns:
        print("FAIL: Column names or column order differ.")
        return False

    excel_normalized = normalize_frame(excel_df)
    parquet_normalized = normalize_frame(parquet_df)

    try:
        pd.testing.assert_frame_equal(
            excel_normalized.reset_index(drop=True),
            parquet_normalized.reset_index(drop=True),
            check_dtype=False,
            check_like=False,
        )

        print("PASS: All values match after normalization.")
        print("Boolean values and missing values were normalized.")
        print('Literal case ID "NA" was preserved as text.')
        return True

    except AssertionError as exc:
        print("FAIL: Differences remain after normalization.")
        print(str(exc)[:2000])
        return False


def main():
    if not EXCEL_PATH.exists():
        raise FileNotFoundError(
            f"Excel file not found: {EXCEL_PATH}"
        )

    excel_df = pd.read_excel(
        EXCEL_PATH,
        keep_default_na=False,
        na_values=[""],
    )

    parquet_df = load_source_parquet()

    required_columns = {CASE_COL, ACTIVITY_COL, TIME_COL}

    for name, df in [
        ("Excel copy", excel_df),
        ("Parquet file", parquet_df),
    ]:
        missing_columns = required_columns - set(df.columns)

        if missing_columns:
            raise ValueError(
                f"{name} is missing required columns: {missing_columns}"
            )

        summarize(name, df)

    passed = compare_datasets(excel_df, parquet_df)

    if not passed:
        raise SystemExit(
            "\nValidation failed. Review the differences before proceeding."
        )

    print("\n========== VALIDATION COMPLETE ==========")
    print("Excel and Parquet match after normalization.")
    print("No source files were modified.")

if __name__ == "__main__":
    main()