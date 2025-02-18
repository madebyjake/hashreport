"""Tests for the compare report handler."""

import pytest

from hashreport.reports.compare_handler import (
    ChangeType,
    ColumnNotFoundError,
    CompareReportHandler,
    EmptyReportError,
)


@pytest.fixture
def sample_data():
    """Sample report data fixture."""
    return [
        {"File Name": "test1.txt", "File Path": "/path/to", "Hash": "abc123"},
        {"File Name": "test2.txt", "File Path": "/path/to", "Hash": "def456"},
    ]


def test_compare_empty_reports():
    """Test comparing empty reports raises error."""
    handler = CompareReportHandler()
    with pytest.raises(EmptyReportError):
        handler.compare_reports([], [])


def test_compare_missing_columns(sample_data):
    """Test comparing reports with missing columns raises error."""
    handler = CompareReportHandler()
    bad_data = [{"Wrong": "data"}]
    with pytest.raises(ColumnNotFoundError):
        handler.compare_reports(sample_data, bad_data)


def test_compare_reports(sample_data):
    """Test basic report comparison."""
    handler = CompareReportHandler()
    new_data = [
        {
            "File Name": "test1.txt",
            "File Path": "/path/to",
            "Hash": "xyz789",
        },  # Modified
        {
            "File Name": "test3.txt",
            "File Path": "/path/to",
            "Hash": "def456",
        },  # Added/Moved
    ]

    changes = handler.compare_reports(sample_data, new_data)

    assert len(changes) == 3
    assert any(
        c.change_type == ChangeType.MODIFIED and c.path == "test1.txt" for c in changes
    )
    assert any(
        c.change_type == ChangeType.REMOVED and c.path == "test2.txt" for c in changes
    )
    assert any(
        c.change_type == ChangeType.MOVED and c.path == "test3.txt" for c in changes
    )


def test_output_filename():
    """Test comparison output filename generation."""
    handler = CompareReportHandler()
    out = handler.get_output_filename(
        "hashreport_250203-1054.csv", "hashreport_250203-1055.csv", "/tmp"
    )
    assert str(out).endswith("compare_hashreport_250203-1054_250203-1055.csv")
