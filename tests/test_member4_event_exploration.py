import pandas as pd
import pytest

from src.member4_event_exploration import (
    DEFAULT_DATASET,
    activity_frequencies,
    analyze_patient_journeys,
    calculate_waiting_times,
    clean_column_names,
    find_column,
    identify_event_columns,
    load_event_dataset,
    normalize_name,
    validate_event_data,
)


def test_normalize_name():
    assert normalize_name(" Case:concept:name ") == "case_concept_name"


def test_find_event_columns():
    columns = ["case:concept:name", "concept:name", "time:timestamp"]

    assert find_column(columns, "case") == "case:concept:name"
    assert find_column(columns, "activity") == "concept:name"
    assert find_column(columns, "timestamp") == "time:timestamp"


def test_clean_column_names_rejects_collisions():
    with pytest.raises(ValueError, match="not unique"):
        clean_column_names(pd.DataFrame(columns=["Case ID", "case_id"]))


def test_identify_event_columns_requires_all_fields():
    with pytest.raises(ValueError, match="timestamp"):
        identify_event_columns(pd.DataFrame(columns=["Case ID", "Activity"]))


def test_validate_event_data_reports_missing_invalid_and_duplicates():
    events = pd.DataFrame(
        {
            "case:concept:name": ["A", "A", "A", "A", None, "B"],
            "concept:name": [
                "Registration",
                "Registration",
                "Triage",
                "Registration",
                "Orphan",
                "Lab",
            ],
            "time:timestamp": [
                "2025-01-01 09:00",
                "2025-01-01 09:00",
                "2025-01-01 09:10",
                "2025-01-01T09:00:00",
                "2025-01-01 09:20",
                "not a timestamp",
            ],
        }
    )

    result = validate_event_data(events)

    assert result["rows"] == 6
    assert result["missing_case_ids"] == 1
    assert result["missing_activities"] == 0
    assert result["missing_timestamps"] == 0
    assert result["invalid_timestamps"] == 1
    assert result["exact_duplicate_rows"] == 1
    assert result["duplicate_event_keys"] == 2
    assert result["case_count"] == 2


def test_patient_journeys_sort_events_and_exclude_incomplete_records():
    events = pd.DataFrame(
        {
            "Case ID": ["A", "A", None, "A"],
            "Activity Name": ["Triage", "Registration", "Orphan", "Unknown time"],
            "Timestamp": [
                "2025-01-01 09:10",
                "2025-01-01 09:00",
                "2025-01-01 09:05",
                "invalid",
            ],
        }
    )

    journeys = analyze_patient_journeys(events)

    assert len(journeys) == 1
    assert journeys.iloc[0]["case_id"] == "A"
    assert journeys.iloc[0]["activities"] == ("Registration", "Triage")
    assert journeys.iloc[0]["duration_minutes"] == 10


def test_activity_frequencies_counts_valid_activity_values():
    events = pd.DataFrame(
        {
            "case_id": ["A", "A", "B"],
            "activity_name": ["Triage", "Lab", "Triage"],
            "timestamp": ["2025-01-01", "2025-01-02", "2025-01-03"],
        }
    )

    frequencies = activity_frequencies(events).set_index("activity")["event_count"]

    assert frequencies.to_dict() == {"Triage": 2, "Lab": 1}


def test_waiting_times_are_chronological_and_grouped_by_case():
    events = pd.DataFrame(
        {
            "case_id": ["A", "B", "A"],
            "activity_name": ["Triage", "Registration", "Registration"],
            "timestamp": [
                "2025-01-01 09:10",
                "2025-01-01 09:00",
                "2025-01-01 09:00",
            ],
        }
    )

    waits = calculate_waiting_times(events)

    assert len(waits) == 1
    assert waits.iloc[0]["case_id"] == "A"
    assert waits.iloc[0]["previous_activity"] == "Registration"
    assert waits.iloc[0]["activity"] == "Triage"
    assert waits.iloc[0]["wait_minutes"] == 10


def test_project_event_dataset_loads():
    assert DEFAULT_DATASET.is_file()
    dataframe = load_event_dataset()

    assert not dataframe.empty
    assert len(dataframe.columns) == 32
    assert identify_event_columns(dataframe) == {
        "case": "case:concept:name",
        "activity": "concept:name",
        "timestamp": "time:timestamp",
    }
