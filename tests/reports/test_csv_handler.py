"""Tests for the CSV report handler."""

from pathlib import Path

import pytest

from hashreport.reports.csv_handler import CSVReportHandler
from hashreport.utils.exceptions import ReportError


@pytest.fixture
def sample_data():
    """Sample data fixture."""
    return [{"name": "test1", "value": "1"}, {"name": "test2", "value": "2"}]


def test_csv_read_write(tmp_path, sample_data):
    """Test CSV read and write."""
    filepath = tmp_path / "test.csv"
    handler = CSVReportHandler(filepath)

    handler.write(sample_data)

    if not filepath.exists():
        pytest.fail("Expected the CSV file to exist after writing")

    read_data = handler.read()
    if len(read_data) != len(sample_data):
        pytest.fail("Read data length does not match sample data")
    if not all(item in sample_data for item in read_data):
        pytest.fail("Some items in read_data are not in sample_data")


def test_csv_append(tmp_path):
    """Test CSV append functionality."""
    filepath = tmp_path / "test.csv"
    handler = CSVReportHandler(filepath)

    entry = {"name": "test1", "value": "1"}
    handler.append(entry)

    second_entry = {"name": "test2", "value": "2"}
    handler.append(second_entry)

    read_data = handler.read()
    if len(read_data) != 2:
        pytest.fail("Expected two entries in CSV after appending")
    if read_data[0] != entry:
        pytest.fail("First entry does not match appended entry")
    if read_data[1] != second_entry:
        pytest.fail("Second entry does not match appended entry")


def test_csv_write_empty(tmp_path):
    """Test writing an empty list."""
    handler = CSVReportHandler(tmp_path / "test.csv")
    handler.write([])
    if handler.filepath.exists():
        pytest.fail("Expected no CSV file to exist after writing empty data")


def test_csv_read_invalid():
    """Test reading from an invalid path."""
    handler = CSVReportHandler("nonexistent.csv")
    with pytest.raises(ReportError):
        handler.read()


def test_csv_write_invalid_path(tmp_path, monkeypatch):
    """Test that writing to an invalid path raises ReportError."""
    handler = CSVReportHandler(tmp_path / "invalid" / "path" / "test.csv")

    def mock_exists(*args, **kwargs):
        return False

    def mock_mkdir(*args, **kwargs):
        raise PermissionError("Access denied")

    monkeypatch.setattr(Path, "exists", mock_exists)
    monkeypatch.setattr(Path, "mkdir", mock_mkdir)

    with pytest.raises(ReportError) as exc_info:
        handler.write([{"test": "data"}])
    if "Failed to create directory" not in str(exc_info.value):
        pytest.fail(
            "Expected 'Failed to create directory' text in the exception message"
        )
