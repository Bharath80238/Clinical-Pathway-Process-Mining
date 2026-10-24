"""Pandas-based exploration of the CareFlow event log."""

from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import Iterable

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATASET = PROJECT_ROOT / "data" / "raw" / "events.xlsx"

_COLUMN_ALIASES = {
    "case": {"case", "caseid", "case_id", "case_concept_name"},
    "activity": {"activity", "activity_name", "event", "concept_name"},
    "timestamp": {"time", "datetime", "timestamp", "time_timestamp"},
}


def normalize_name(name: object) -> str:
    """Normalize a field name to lowercase snake_case."""
    normalized = re.sub(r"[^a-zA-Z0-9]+", "_", str(name).strip().lower())
    return normalized.strip("_")


def find_column(columns: Iterable[object], target: str) -> object | None:
    """Find a source column matching a case, activity, or timestamp field."""
    aliases = _COLUMN_ALIASES.get(target, {normalize_name(target)})
    for column in columns:
        if normalize_name(column) in aliases:
            return column
    return None


def clean_column_names(dataframe: pd.DataFrame) -> pd.DataFrame:
    """Return a copy with normalized column names, rejecting name collisions."""
    cleaned = [normalize_name(column) for column in dataframe.columns]
    duplicates = pd.Index(cleaned)[pd.Index(cleaned).duplicated()].unique().tolist()
    if duplicates:
        raise ValueError(
            "Column names are not unique after normalization: "
            + ", ".join(duplicates)
        )
    result = dataframe.copy()
    result.columns = cleaned
    return result


def identify_event_columns(dataframe: pd.DataFrame) -> dict[str, str]:
    """Return source names for the required case, activity, and timestamp fields."""
    columns = {
        key: find_column(dataframe.columns, key)
        for key in ("case", "activity", "timestamp")
    }
    missing = [key for key, column in columns.items() if column is None]
    if missing:
        raise ValueError(
            "Could not identify required event column(s): " + ", ".join(missing)
        )
    return {key: str(column) for key, column in columns.items()}


def load_event_dataset(file_path: str | Path = DEFAULT_DATASET) -> pd.DataFrame:
    """Load a CSV or Excel event dataset."""
    path = Path(file_path)
    if not path.is_file():
        raise FileNotFoundError(f"Dataset file not found: {path}")
    if path.suffix.lower() == ".csv":
        return pd.read_csv(path)
    if path.suffix.lower() in {".xlsx", ".xls"}:
        return pd.read_excel(path)
    raise ValueError(f"Unsupported dataset format: {path.suffix}")


def _normalized_event_columns(dataframe: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, str]]:
    cleaned = clean_column_names(dataframe)
    columns = identify_event_columns(cleaned)
    return cleaned, columns


def _parse_timestamps(values: pd.Series) -> pd.Series:
    parsed = pd.to_datetime(values, errors="coerce")
    unparsed = values.notna() & parsed.isna()
    if unparsed.any():
        parsed.loc[unparsed] = values.loc[unparsed].map(
            lambda value: pd.to_datetime(value, errors="coerce")
        )
    return parsed


def validate_event_data(dataframe: pd.DataFrame) -> dict[str, object]:
    """Summarize missing values, duplicate events, and timestamp validity."""
    cleaned, columns = _normalized_event_columns(dataframe)
    timestamp_values = cleaned[columns["timestamp"]]
    parsed_timestamps = _parse_timestamps(timestamp_values)
    missing_case_ids = int(cleaned[columns["case"]].isna().sum())
    missing_activities = int(cleaned[columns["activity"]].isna().sum())
    missing_timestamps = int(timestamp_values.isna().sum())
    invalid_timestamps = int(
        (parsed_timestamps.isna() & timestamp_values.notna()).sum()
    )
    event_key = [
        columns["case"],
        columns["activity"],
        columns["timestamp"],
    ]
    complete_events = cleaned.copy()
    complete_events[columns["timestamp"]] = parsed_timestamps
    complete_events = complete_events.dropna(subset=event_key)

    return {
        "rows": int(len(cleaned)),
        "columns": int(len(cleaned.columns)),
        "missing_values": {
            str(column): int(count)
            for column, count in cleaned.isna().sum().items()
            if count
        },
        "missing_case_ids": missing_case_ids,
        "missing_activities": missing_activities,
        "missing_timestamps": missing_timestamps,
        "invalid_timestamps": invalid_timestamps,
        "exact_duplicate_rows": int(cleaned.duplicated().sum()),
        "duplicate_event_keys": int(complete_events.duplicated(event_key).sum()),
        "case_count": int(cleaned[columns["case"]].nunique()),
        "activity_count": int(cleaned[columns["activity"]].nunique()),
        "timestamp_start": parsed_timestamps.min(),
        "timestamp_end": parsed_timestamps.max(),
    }


def analyze_patient_journeys(dataframe: pd.DataFrame) -> pd.DataFrame:
    """Build ordered activity sequences and durations for complete event records."""
    cleaned, columns = _normalized_event_columns(dataframe)
    cleaned[columns["timestamp"]] = _parse_timestamps(cleaned[columns["timestamp"]])
    valid = cleaned.dropna(
        subset=[columns["case"], columns["activity"], columns["timestamp"]]
    ).sort_values([columns["case"], columns["timestamp"]], kind="stable")
    valid = valid.reset_index(drop=True)

    journeys = []
    for case_id, events in valid.groupby(columns["case"], sort=False):
        start = events[columns["timestamp"]].iloc[0]
        end = events[columns["timestamp"]].iloc[-1]
        journeys.append(
            {
                "case_id": case_id,
                "event_count": int(len(events)),
                "activities": tuple(events[columns["activity"]].tolist()),
                "start_time": start,
                "end_time": end,
                "duration_minutes": (end - start).total_seconds() / 60,
            }
        )
    return pd.DataFrame(
        journeys,
        columns=[
            "case_id",
            "event_count",
            "activities",
            "start_time",
            "end_time",
            "duration_minutes",
        ],
    )


def activity_frequencies(dataframe: pd.DataFrame) -> pd.DataFrame:
    """Count events per activity, excluding rows without an activity value."""
    cleaned, columns = _normalized_event_columns(dataframe)
    counts = cleaned[columns["activity"]].dropna().value_counts()
    return counts.rename_axis("activity").reset_index(name="event_count")


def calculate_waiting_times(dataframe: pd.DataFrame) -> pd.DataFrame:
    """Calculate elapsed minutes between consecutive valid events per case."""
    cleaned, columns = _normalized_event_columns(dataframe)
    cleaned[columns["timestamp"]] = _parse_timestamps(cleaned[columns["timestamp"]])
    valid = cleaned.dropna(
        subset=[columns["case"], columns["activity"], columns["timestamp"]]
    ).sort_values([columns["case"], columns["timestamp"]], kind="stable")
    valid = valid.reset_index(drop=True)

    grouped = valid.groupby(columns["case"], sort=False)
    transitions = pd.DataFrame(
        {
            "case_id": valid[columns["case"]],
            "previous_activity": grouped[columns["activity"]].shift(),
            "activity": valid[columns["activity"]],
            "previous_timestamp": grouped[columns["timestamp"]].shift(),
            "timestamp": valid[columns["timestamp"]],
        },
        index=valid.index,
    )
    transitions["wait_minutes"] = (
        transitions["timestamp"] - transitions["previous_timestamp"]
    ).dt.total_seconds() / 60
    return transitions.dropna(subset=["previous_timestamp"]).reset_index(drop=True)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Explore the CareFlow event dataset."
    )
    parser.add_argument(
        "dataset",
        nargs="?",
        type=Path,
        default=DEFAULT_DATASET,
        help=f"CSV or Excel dataset (default: {DEFAULT_DATASET})",
    )
    args = parser.parse_args()

    dataframe = load_event_dataset(args.dataset)
    quality = validate_event_data(dataframe)
    journeys = analyze_patient_journeys(dataframe)
    frequencies = activity_frequencies(dataframe)
    waits = calculate_waiting_times(dataframe)["wait_minutes"]

    print(f"Dataset: {args.dataset}")
    print(
        f"Rows: {quality['rows']}; columns: {quality['columns']}; "
        f"cases: {quality['case_count']}; activities: {quality['activity_count']}"
    )
    print(
        "Data quality: "
        f"missing case IDs={quality['missing_case_ids']}, "
        f"missing activities={quality['missing_activities']}, "
        f"missing timestamps={quality['missing_timestamps']}, "
        f"invalid timestamps={quality['invalid_timestamps']}, "
        f"exact duplicate rows={quality['exact_duplicate_rows']}, "
        f"duplicate event keys={quality['duplicate_event_keys']}"
    )
    print("\nMost frequent activities:")
    print(frequencies.head(10).to_string(index=False))
    print(f"\nPatient journeys reconstructed: {len(journeys)}")
    if not waits.empty:
        print(
            "Consecutive-event waiting time (minutes): "
            f"count={len(waits)}, median={waits.median():.2f}, "
            f"mean={waits.mean():.2f}, p90={waits.quantile(0.9):.2f}"
        )


if __name__ == "__main__":
    main()
