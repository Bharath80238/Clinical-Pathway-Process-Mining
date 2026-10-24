
from src.member4_event_exploration import (
    normalize_name,
    find_column,
)


def test_normalize_name():
    assert normalize_name("Case ID") == "case_id"


def test_find_case_column():
    columns = ["Case ID", "Activity Name", "Timestamp"]

    assert find_column(columns, "case") == "Case ID"


def test_find_activity_column():
    columns = ["Case ID", "Activity Name", "Timestamp"]

    assert find_column(columns, "activity") == "Activity Name"


def test_find_timestamp_column():
    columns = ["Case ID", "Activity Name", "Timestamp"]

    assert find_column(columns, "timestamp") == "Timestamp"


def test_missing_column_returns_none():
    assert find_column(["Order ID"], "case") is None
