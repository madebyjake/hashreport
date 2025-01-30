"""Tests for the scanner utility."""

from unittest.mock import MagicMock, patch

import pytest

from hashreport.utils.scanner import (
    count_files,
    get_report_filename,
    get_report_handlers,
    walk_directory_and_log,
)


def test_get_report_filename(tmp_path):
    """Test generating a report filename if provided path is a directory."""
    dir_path = tmp_path
    filename = get_report_filename(str(dir_path))
    if not filename.endswith(".csv"):
        pytest.fail("Expected default .csv extension when no suffix is specified")


@patch("hashreport.utils.scanner.os.walk")
@patch(
    "hashreport.utils.scanner.calculate_hash",
    return_value=("test.txt", "abc123", "2025-01-01 00:00:00"),
)
@patch("hashreport.utils.scanner.get_report_handlers")
@patch("hashreport.utils.scanner.os.path.getsize", return_value=1024)
@patch("hashreport.utils.scanner.os.path.getctime", return_value=1706317261.0)
def test_walk_directory_and_log(
    mock_getctime,
    mock_getsize,
    mock_handlers,
    mock_calculate_hash,
    mock_oswalk,
    tmp_path,
):
    """Test a simplified walk_directory_and_log."""
    # Create test files
    test_file = tmp_path / "file1.txt"
    test_file.touch()

    mock_oswalk.return_value = [
        (str(tmp_path), ["dir1"], ["file1.txt", "file2.txt"]),
    ]
    mock_handler = MagicMock()
    mock_handlers.return_value = [mock_handler]
    mock_calculate_hash.return_value = (str(test_file), "abc123", "2025-01-01 00:00:00")

    walk_directory_and_log(str(tmp_path), str(tmp_path / "out_report.csv"))

    mock_handler.write.assert_called_once()
    args = mock_handler.write.call_args[0]
    assert len(args[0]) == 2  # Should have 2 file entries
    assert args[0][0]["File Name"] == "file1.txt"


def test_get_report_filename_with_timestamp(tmp_path):
    """Test report filename generation with timestamp."""
    result = get_report_filename(str(tmp_path))
    if not result.startswith(str(tmp_path)):
        pytest.fail("Expected path to start with tmp_path")
    if "hashreport_" not in result:
        pytest.fail("Expected 'hashreport_' in filename")
    if not result.endswith(".csv"):
        pytest.fail("Expected .csv extension")


def test_get_report_filename_existing_path(tmp_path):
    """Test report filename with existing path."""
    path = tmp_path / "report.json"
    result = get_report_filename(str(path), output_format="json")
    assert (
        str(path.with_suffix(".json")) == result
    ), "Expected path with .json extension"


def test_get_report_filename_with_format(tmp_path):
    """Test report filename generation with explicit format."""
    result = get_report_filename(str(tmp_path), output_format="json")
    assert result.endswith(
        ".json"
    ), "Expected .json extension when json format specified"
    assert "hashreport_" in result, "Expected hashreport_ prefix"

    result = get_report_filename(str(tmp_path), output_format="csv")
    assert result.endswith(".csv"), "Expected .csv extension when csv format specified"


def test_get_report_filename_format_override(tmp_path):
    """Test that format parameter overrides existing extension."""
    path = tmp_path / "report.csv"
    result = get_report_filename(str(path), output_format="json")
    assert result.endswith(
        ".json"
    ), "Expected format override to change extension to .json"


@patch("hashreport.utils.scanner.calculate_hash")
def test_walk_directory_with_filters(mock_hash, tmp_path):
    """Test directory walking with filters."""
    mock_hash.return_value = ("test.txt", "abc123", "2024-01-01 00:00:00")

    # Create test files
    (tmp_path / "test.txt").touch()
    (tmp_path / "skip.txt").touch()
    (tmp_path / "test.pdf").touch()

    exclude_paths = {str(tmp_path / "skip.txt")}
    file_extension = ".txt"

    output = tmp_path / "report.csv"
    walk_directory_and_log(
        str(tmp_path),
        str(output),
        exclude_paths=exclude_paths,
        file_extension=file_extension,
    )

    # Should process only test.txt
    if mock_hash.call_count != 1:
        pytest.fail("Expected exactly one file to be processed")


def test_walk_directory_with_specific_files(tmp_path):
    """Test processing specific files only."""
    test_file = tmp_path / "specific.txt"
    test_file.touch()

    specific_files = {str(test_file)}
    output = tmp_path / "report.csv"

    walk_directory_and_log(str(tmp_path), str(output), specific_files=specific_files)

    if not output.exists():
        pytest.fail("Expected output file to be created")


@patch("hashreport.utils.scanner.os.walk")
@patch("hashreport.utils.scanner.calculate_hash")
@patch("hashreport.utils.scanner.ProgressBar")
def test_multiple_report_formats(mock_progress, mock_hash, mock_walk, tmp_path, capfd):
    """Test handling multiple report formats."""
    test_file = tmp_path / "test.txt"
    test_file.touch()  # Create the test file

    mock_walk.return_value = [(str(tmp_path), [], ["test.txt"])]
    mock_hash.return_value = (str(test_file), "abc123", "2024-01-01 00:00:00")

    report_paths = [str(tmp_path / "report.json"), str(tmp_path / "report.csv")]
    walk_directory_and_log(str(tmp_path), report_paths)

    captured = capfd.readouterr()
    assert "Reports saved to:" in captured.out
    assert "report.json" in captured.out
    assert "report.csv" in captured.out


def test_get_report_handlers():
    """Test creating multiple report handlers."""
    filenames = ["test.json", "test.csv"]
    handlers = get_report_handlers(filenames)

    assert len(handlers) == 2
    from hashreport.reports.csv_handler import CSVReportHandler
    from hashreport.reports.json_handler import JSONReportHandler

    assert isinstance(handlers[0], JSONReportHandler)
    assert isinstance(handlers[1], CSVReportHandler)


def test_count_files(tmp_path):
    """Test counting files in directory."""
    # Create test files
    (tmp_path / "test1.txt").write_text("test")
    (tmp_path / "test2.txt").write_text("test")

    # Create nested files
    nested = tmp_path / "nested"
    nested.mkdir()
    (nested / "test3.txt").write_text("test")

    # Test recursive counting
    assert count_files(tmp_path, recursive=True) == 3

    # Test non-recursive counting
    assert count_files(tmp_path, recursive=False) == 2
    assert count_files(tmp_path, recursive=True) == 3

    # Test non-recursive counting
    assert count_files(tmp_path, recursive=False) == 2

    assert count_files(tmp_path, recursive=False) == 2
    assert count_files(tmp_path, recursive=True) == 3

    # Test non-recursive counting
    assert count_files(tmp_path, recursive=False) == 2
