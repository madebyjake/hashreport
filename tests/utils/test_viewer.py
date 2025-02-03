"""Tests for report viewer."""

import io
from unittest.mock import MagicMock, patch

import pytest
from rich.console import Console

from hashreport.reports.compare_handler import ChangeType, FileChange
from hashreport.utils.exceptions import ReportError
from hashreport.utils.viewer import ReportViewer


@pytest.fixture
def sample_report_data():
    """Sample report data fixture."""
    return [
        {
            "File Name": "test1.txt",
            "File Path": "/path/to",
            "Hash": "abc123",
            "Size": "1KB",
        },
        {
            "File Name": "test2.txt",
            "File Path": "/path/to",
            "Hash": "def456",
            "Size": "2KB",
        },
    ]


@pytest.fixture
def sample_comparison():
    """Sample comparison data fixture."""
    return [
        FileChange(
            type=ChangeType.MODIFIED,
            path="test1.txt",
            old_hash="abc123",
            new_hash="xyz789",
            old_path="/path/to",
            new_path="/path/to",
        ),
        FileChange(
            type=ChangeType.MOVED,
            path="test2.txt",
            old_hash="def456",
            new_hash="def456",
            old_path="/path/to",
            new_path="/new/path",
        ),
        FileChange(
            type=ChangeType.ADDED,
            path="test3.txt",
            new_hash="ghi789",
            new_path="/path/to",
        ),
        FileChange(
            type=ChangeType.REMOVED,
            path="test4.txt",
            old_hash="jkl012",
            old_path="/path/to",
        ),
    ]


@pytest.fixture
def mock_file(tmp_path, sample_report_data):
    """Create a mock report file."""
    import csv

    file_path = tmp_path / "test.csv"
    with open(file_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=sample_report_data[0].keys())
        writer.writeheader()
        writer.writerows(sample_report_data)
    return file_path


def test_view_report(mock_file):
    """Test basic report viewing."""
    viewer = ReportViewer()
    console = Console(file=io.StringIO(), force_terminal=True)
    viewer.console = console

    with patch.object(console, "pager") as mock_pager:
        mock_pager.__enter__ = MagicMock()
        mock_pager.__exit__ = MagicMock()
        viewer.display_report(mock_file)

        output = console.file.getvalue()
        # Use less strict assertions that ignore formatting
        assert "test1.txt" in output
        assert "test2.txt" in output
        assert "Total entries: 2" in output.replace("\x1b[1;36m", "").replace(
            "\x1b[0m", ""
        )


def test_view_report_with_filter(mock_file):
    """Test report viewing with filter."""
    viewer = ReportViewer()
    console = Console(file=io.StringIO(), force_terminal=True)
    viewer.console = console

    with patch.object(console, "pager") as mock_pager:
        mock_pager.__enter__ = MagicMock()
        mock_pager.__exit__ = MagicMock()
        viewer.display_report(mock_file, filter_text="test1")

        output = console.file.getvalue()
        assert "test1.txt" in output
        assert "test2.txt" not in output
        assert "Total entries: 1" in output.replace("\x1b[1;36m", "").replace(
            "\x1b[0m", ""
        )


def test_display_comparison(sample_comparison):
    """Test comparison display."""
    viewer = ReportViewer()
    console = Console(file=io.StringIO(), force_terminal=True)
    viewer.console = console

    with patch.object(console, "pager") as mock_pager:
        mock_pager.__enter__ = MagicMock()
        mock_pager.__exit__ = MagicMock()
        viewer.display_comparison(sample_comparison)

        output = console.file.getvalue()
        # Check all change types are present
        assert "modified" in output.lower()
        assert "moved" in output.lower()
        assert "added" in output.lower()
        assert "removed" in output.lower()
        # Check file details
        assert "test1.txt" in output
        assert "Hash changed" in output
        assert "File moved" in output
        assert "Total changes: 4" in output.replace("\x1b[1;36m", "").replace(
            "\x1b[0m", ""
        )


def test_invalid_file_format():
    """Test handling of invalid file formats."""
    viewer = ReportViewer()
    with pytest.raises(ReportError, match="Unsupported file format"):
        viewer.display_report("test.invalid")


def test_save_comparison(tmp_path, sample_comparison):
    """Test saving comparison results."""
    viewer = ReportViewer()
    output_dir = tmp_path / "output"
    report1 = "hashreport_250203-1020.csv"
    report2 = "hashreport_250203-1021.csv"

    viewer.save_comparison(sample_comparison, output_dir, report1, report2)

    # Check output file exists and has expected name
    expected_file = output_dir / "compare_hashreport_250203-1020_250203-1021.csv"
    assert expected_file.exists()

    # Verify file contents using string values
    import csv

    with open(expected_file, newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        assert len(rows) == 4
        # Use exact string matches based on ChangeType enum string values
        expected_types = {"modified", "moved", "added", "removed"}
        change_types = {r["Change Type"].lower() for r in rows}
        assert change_types == expected_types
