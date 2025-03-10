"""Tests for the JSON report handler."""

from pathlib import Path

import pytest

from hashreport.reports.json_handler import JSONReportHandler
from hashreport.utils.exceptions import ReportError


@pytest.fixture
def sample_data():
    """Sample data fixture."""
    return [
        {"file": "test1.txt", "name": "test1", "value": 1},
        {"file": "test2.txt", "name": "test2", "value": 2},
    ]


def test_json_read_write(tmp_path, sample_data):
    """Test JSON read and write."""
    filepath = tmp_path / "test.json"
    handler = JSONReportHandler(filepath)

    handler.write(sample_data)
    if not filepath.exists():
        pytest.fail("Expected the JSON file to exist after writing")

    read_data = handler.read()
    if read_data != sample_data:
        pytest.fail("Read data does not match the sample data")


def test_json_append(tmp_path):
    """Test JSON append functionality."""
    filepath = tmp_path / "test.json"
    handler = JSONReportHandler(filepath)

    entry = {"file": "test1.txt", "name": "test1", "value": 1}
    handler.append(entry)

    read_data = handler.read()
    if len(read_data) != 1:
        pytest.fail("Expected a single entry in JSON after appending")
    if read_data[0] != entry:
        pytest.fail("Appended entry does not match the original entry")


def test_json_read_invalid(tmp_path, monkeypatch):
    """Test reading invalid or nonexistent paths."""
    handler = JSONReportHandler("nonexistent.json")
    assert handler.read() == []  # Should return empty list for nonexistent file

    def mock_mkdir():
        raise PermissionError("Access denied")

    handler = JSONReportHandler(tmp_path / "invalid" / "path" / "test.json")
    monkeypatch.setattr(Path, "mkdir", mock_mkdir)

    with pytest.raises(ReportError):
        handler.write([{"file": "test.txt", "test": "data"}])


def test_json_single_object(tmp_path):
    """Test writing and reading a single JSON object."""
    handler = JSONReportHandler(tmp_path / "test.json")
    single_entry = {"file": "test.txt", "name": "test"}

    handler.write([single_entry])
    read_data = handler.read()

    if not isinstance(read_data, list):
        pytest.fail("Expected returned data to be a list")
    if len(read_data) != 1:
        pytest.fail("Expected exactly one entry in JSON")
