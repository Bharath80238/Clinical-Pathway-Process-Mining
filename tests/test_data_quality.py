from io import BytesIO
import pandas as pd
import pytest
from src import data_quality

def create_sample_dataset():
    """Create a small source-like dataset for validation tests."""
    return pd.DataFrame({
        data_quality.CASE_COL: ["CASE_001", "NA"],
        "InfectionSuspected": [1.0, None],
        "Age": [65.0, 72.0],
        data_quality.ACTIVITY_COL: ["ER Registration", "Leucocytes"],
        data_quality.TIME_COL: pd.to_datetime([
            "2024-01-01 10:00:00",
            "2024-01-01 11:00:00",
        ]),
    })

def test_normalize_boolean_values():
    assert data_quality.normalize_boolean(1.0) == "TRUE"
    assert data_quality.normalize_boolean(0.0) == "FALSE"
    assert data_quality.normalize_boolean(True) == "TRUE"
    assert data_quality.normalize_boolean(False) == "FALSE"

def test_normalize_boolean_preserves_missing_values():
    assert data_quality.normalize_boolean(float("nan")) == "<MISSING>"
    assert data_quality.normalize_boolean(None) == "<MISSING>"

def test_normalize_boolean_does_not_accept_unexpected_values():
    assert data_quality.normalize_boolean(2) == "2"
    assert data_quality.normalize_boolean("unknown") == "UNKNOWN"

def test_normalize_frame_preserves_literal_na_case_id():
    dataset = create_sample_dataset()
    result = data_quality.normalize_frame(dataset)
    assert result.loc[1, data_quality.CASE_COL] == "NA"
    assert result.loc[0, data_quality.CASE_COL] == "CASE_001"

def test_normalize_frame_standardizes_timestamps_to_utc():
    dataset = create_sample_dataset()
    result = data_quality.normalize_frame(dataset)
    assert result.loc[0, data_quality.TIME_COL] == (
        "2024-01-01 10:00:00+00:00"
    )

def test_compare_datasets_accepts_equivalent_boolean_representations(
    capsys,
):
    excel = create_sample_dataset()
    parquet = excel.copy()
    parquet["InfectionSuspected"] = pd.Series(
        [True, None],
        dtype=object,
    )
    parquet[data_quality.TIME_COL] = pd.to_datetime(
        parquet[data_quality.TIME_COL],
        utc=True,
    )
    assert data_quality.compare_datasets(excel, parquet) is True
    output = capsys.readouterr().out
    assert "PASS: All values match after normalization." in output

def test_compare_datasets_rejects_different_values(capsys):
    excel = create_sample_dataset()
    parquet = excel.copy()
    parquet.loc[0, "Age"] = 99.0
    assert data_quality.compare_datasets(excel, parquet) is False
    output = capsys.readouterr().out
    assert "FAIL: Differences remain after normalization." in output

def test_compare_datasets_rejects_reordered_rows(capsys):
    excel = create_sample_dataset()
    parquet = excel.iloc[::-1].reset_index(drop=True)
    assert data_quality.compare_datasets(excel, parquet) is False
    output = capsys.readouterr().out
    assert "FAIL: Differences remain after normalization." in output

def test_compare_datasets_rejects_different_column_order(capsys):
    excel = create_sample_dataset()
    parquet = excel[list(reversed(excel.columns))]
    assert data_quality.compare_datasets(excel, parquet) is False
    output = capsys.readouterr().out
    assert "FAIL: Column names or column order differ." in output

def test_load_source_parquet_downloads_and_saves_valid_file(
    tmp_path, monkeypatch
):
    dataset = pd.DataFrame({
        data_quality.CASE_COL: ["CASE_001"],
        data_quality.ACTIVITY_COL: ["ER Registration"],
        data_quality.TIME_COL: pd.to_datetime([
            "2024-01-01 10:00:00"
        ]),
    })
    buffer = BytesIO()
    dataset.to_parquet(buffer, index=False)
    parquet_bytes = buffer.getvalue()
    class FakeResponse:
        content = parquet_bytes
        def raise_for_status(self):
            pass
    destination = tmp_path / "events.parquet"
    monkeypatch.setattr(data_quality, "PARQUET_PATH", destination)
    monkeypatch.setattr(data_quality, "RAW_DIR", tmp_path)
    monkeypatch.setattr(
        data_quality.requests,
        "get",
        lambda *args, **kwargs: FakeResponse(),
    )
    result = data_quality.load_source_parquet()
    pd.testing.assert_frame_equal(result, dataset)
    assert destination.exists()

def test_load_source_parquet_rejects_download_with_invalid_schema(
    tmp_path, monkeypatch
):
    dataset = pd.DataFrame({"wrong_column": ["x"]})
    buffer = BytesIO()
    dataset.to_parquet(buffer, index=False)
    parquet_bytes = buffer.getvalue()
    class FakeResponse:
        content = parquet_bytes
        def raise_for_status(self):
            pass
    destination = tmp_path / "events.parquet"
    monkeypatch.setattr(data_quality, "PARQUET_PATH", destination)
    monkeypatch.setattr(data_quality, "RAW_DIR", tmp_path)
    monkeypatch.setattr(
        data_quality.requests,
        "get",
        lambda *args, **kwargs: FakeResponse(),
    )
    with pytest.raises(ValueError, match="missing required columns"):
        data_quality.load_source_parquet()
    assert not destination.exists()
    assert list(tmp_path.glob("*.parquet")) == []

def test_load_source_parquet_does_not_save_invalid_download(
    tmp_path, monkeypatch
):
    destination = tmp_path / "events.parquet"
    class FakeResponse:
        content = b"this is not a valid parquet file"
        def raise_for_status(self):
            pass
    monkeypatch.setattr(data_quality, "PARQUET_PATH", destination)
    monkeypatch.setattr(data_quality, "RAW_DIR", tmp_path)
    monkeypatch.setattr(
        data_quality.requests,
        "get",
        lambda *args, **kwargs: FakeResponse(),
    )
    with pytest.raises(ValueError):
        data_quality.load_source_parquet()
    assert not destination.exists()
    assert list(tmp_path.glob("*.parquet")) == []

def test_load_source_parquet_uses_existing_file_without_download(
    tmp_path, monkeypatch
):
    destination = tmp_path / "events.parquet"
    expected = pd.DataFrame({
        "case_id": ["CASE_001"],
        "value": [25],
    })
    expected.to_parquet(destination, index=False)

    def unexpected_download(*args, **kwargs):
        pytest.fail("HTTP download should not occur")
    monkeypatch.setattr(data_quality, "PARQUET_PATH", destination)
    monkeypatch.setattr(
        data_quality.requests,
        "get",
        unexpected_download,
    )
    result = data_quality.load_source_parquet()
    pd.testing.assert_frame_equal(result, expected)

def test_load_source_parquet_handles_http_error(tmp_path, monkeypatch):
    destination = tmp_path / "events.parquet"
    class FakeResponse:
        def raise_for_status(self):
            raise data_quality.requests.HTTPError("404 Not Found")
    monkeypatch.setattr(data_quality, "PARQUET_PATH", destination)
    monkeypatch.setattr(data_quality, "RAW_DIR", tmp_path)
    monkeypatch.setattr(
        data_quality.requests,
        "get",
        lambda *args, **kwargs: FakeResponse(),
    )
    with pytest.raises(data_quality.requests.HTTPError):
        data_quality.load_source_parquet()
    assert not destination.exists()
    assert list(tmp_path.glob("*.parquet")) == []

def test_validate_schema_accepts_valid_dataset():
    dataset = create_sample_dataset()
    assert data_quality.validate_schema(dataset) is True

def test_validate_schema_rejects_missing_required_columns():
    dataset = create_sample_dataset().drop(
        columns=[data_quality.TIME_COL]
    )
    with pytest.raises(ValueError, match="missing required columns"):
        data_quality.validate_schema(dataset)

def test_validate_schema_rejects_duplicate_columns():
    dataset = create_sample_dataset()
    dataset.insert(
        len(dataset.columns),
        data_quality.CASE_COL,
        ["CASE_002", "CASE_003"],
        allow_duplicates=True,
    )
    with pytest.raises(ValueError, match="duplicate columns"):
        data_quality.validate_schema(dataset)
