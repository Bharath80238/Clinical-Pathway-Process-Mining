
from pathlib import Path
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data" / "raw"


def find_event_dataset():
    """Find an Excel or CSV event dataset in data/raw."""
    if not DATA_DIR.exists():
        raise FileNotFoundError(
            f"Dataset folder not found: {DATA_DIR}"
        )

    files = (
        list(DATA_DIR.glob("*.xlsx"))
        + list(DATA_DIR.glob("*.xls"))
        + list(DATA_DIR.glob("*.csv"))
    )

    if not files:
        raise FileNotFoundError(
            f"No Excel or CSV dataset found in {DATA_DIR}"
        )

    return files[0]


def load_event_dataset(file_path):
    """Load an Excel or CSV dataset."""
    file_path = Path(file_path)

    if file_path.suffix.lower() == ".csv":
        return pd.read_csv(file_path)

    return pd.read_excel(file_path)


def test_event_dataset_exists():
    """Check that the event dataset exists."""
    assert find_event_dataset().exists()


def test_event_dataset_loads():
    """Check that the dataset loads and contains data."""
    file_path = find_event_dataset()
    df = load_event_dataset(file_path)

    assert not df.empty, "The event dataset is empty."
    assert len(df.columns) >= 2, (
        "The dataset should contain at least two columns."
    )


def test_event_dataset_has_valid_column_names():
    """Check that column names are not blank."""
    file_path = find_event_dataset()
    df = load_event_dataset(file_path)

    assert all(
        str(column).strip() for column in df.columns
    ), "One or more column names are blank."
