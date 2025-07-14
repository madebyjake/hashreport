"""Tests for the scanner utility."""

from unittest.mock import MagicMock, patch

import pytest

from hashreport.utils.exceptions import HashReportError
from hashreport.utils.scanner import (
    count_files,
    get_report_filename,
    get_report_handlers,
    parse_size_string,
    should_process_file,
    walk_directory_and_log,
)


def test_get_report_filename(tmp_path):
    """Test report filename generation including timestamp and format."""
    # Test default format
    result = get_report_filename(str(tmp_path))
    assert result.endswith(".csv"), "Expected .csv extension by default"
    assert "hashreport_" in result, "Expected 'hashreport_' prefix"

    # Test explicit format
    result = get_report_filename(str(tmp_path), output_format="json")
    assert result.endswith(".json"), "Expected .json extension when specified"

    # Test with existing path
    path = tmp_path / "report.csv"
    result = get_report_filename(str(path), output_format="json")
    assert (
        str(path.with_suffix(".json")) == result
    ), "Expected path with correct extension"


@patch("hashreport.utils.scanner.os.walk")
@patch("hashreport.utils.scanner.calculate_hash")
@patch("hashreport.utils.scanner.ProgressBar")
@patch("hashreport.utils.scanner.get_report_handlers")
def test_walk_directory_and_log(
    mock_handlers,
    mock_progress,
    mock_hash,
    mock_walk,
    tmp_path,
):
    """Test a simplified walk_directory_and_log."""
    # Create test files
    test_file = tmp_path / "file1.txt"
    test_file2 = tmp_path / "file2.txt"
    test_file.touch()
    test_file2.touch()

    mock_walk.return_value = [
        (str(tmp_path), ["dir1"], ["file1.txt", "file2.txt"]),
    ]
    mock_handler = MagicMock()
    mock_handlers.return_value = [mock_handler]
    mock_hash.side_effect = [
        (str(test_file), "abc123", "2025-01-01 00:00:00"),
        (str(test_file2), "def456", "2025-01-01 00:00:00"),
    ]

    # Create a mock progress bar
    mock_pbar = MagicMock()
    mock_progress.return_value = mock_pbar

    walk_directory_and_log(str(tmp_path), str(tmp_path / "out_report.csv"))

    # Verify progress bar was created with show_file_names=False by default
    mock_progress.assert_called_once_with(total=2, show_file_names=False)

    mock_handler.write.assert_called_once()
    args = mock_handler.write.call_args[0]
    assert len(args[0]) == 2  # Should have 2 file entries
    assert args[0][0]["File Name"] == "file1.txt"


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

    # Create a mock progress bar
    mock_pbar = MagicMock()
    mock_progress.return_value = mock_pbar

    report_paths = [str(tmp_path / "report.json"), str(tmp_path / "report.csv")]
    walk_directory_and_log(str(tmp_path), report_paths)

    # Verify progress bar was created with show_file_names=False by default
    mock_progress.assert_called_once_with(total=1, show_file_names=False)

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


def test_should_process_file(tmp_path):
    """Test file processing filters."""
    test_file = tmp_path / "test.txt"
    test_file.touch()

    # Test basic file
    assert should_process_file(str(test_file))

    # Test with extension filter
    assert should_process_file(str(test_file), file_extension=".txt")
    assert not should_process_file(str(test_file), file_extension=".csv")

    # Test with name filter
    assert should_process_file(str(test_file), file_names={"test.txt"})
    assert not should_process_file(str(test_file), file_names={"other.txt"})

    # Test with exclude paths
    assert not should_process_file(str(test_file), exclude_paths={str(test_file)})


def test_parse_size_string_invalid_formats():
    """Test parse_size_string with invalid formats."""
    invalid_sizes = [
        "abc",  # No number
        "123",  # No unit
        "123XYZ",  # Invalid unit
        "abcKB",  # No number
        "1.2.3KB",  # Invalid number
    ]

    for size_str in invalid_sizes:
        with pytest.raises(ValueError):
            parse_size_string(size_str)


def test_parse_size_string_edge_cases():
    """Test parse_size_string with edge cases."""
    # Whitespace handling
    assert parse_size_string("  1KB  ") == 1024
    assert parse_size_string("\t2MB\n") == 2 * 1024 * 1024

    # Zero values
    assert parse_size_string("0B") == 0
    assert parse_size_string("0KB") == 0

    # Large values
    assert parse_size_string("1GB") == 1024 * 1024 * 1024
    assert parse_size_string("2.5MB") == int(2.5 * 1024 * 1024)


def test_get_report_handlers_unsupported_format():
    """Test get_report_handlers with unsupported format."""
    with pytest.raises(HashReportError, match="Unsupported file format"):
        get_report_handlers(["test.txt"])


def test_get_report_filename_directory(tmp_path):
    """Test get_report_filename with directory path."""
    result = get_report_filename(str(tmp_path), "json", "test")
    assert result.endswith(".json")
    assert "test_" in result
    assert result.startswith(str(tmp_path))


def test_get_report_filename_file_path(tmp_path):
    """Test get_report_filename with file path."""
    file_path = tmp_path / "report.csv"
    result = get_report_filename(str(file_path), "json")
    assert result.endswith(".json")
    assert result.startswith(str(tmp_path))


def test_should_process_file_exclude_paths(tmp_path):
    """Test should_process_file with exclude paths."""
    test_file = tmp_path / "test.txt"
    test_file.write_text("test")

    exclude_paths = {str(test_file)}
    assert not should_process_file(str(test_file), exclude_paths=exclude_paths)

    # Should process when not in exclude list
    assert should_process_file(str(test_file), exclude_paths=set())


def test_should_process_file_extension_filter(tmp_path):
    """Test should_process_file with extension filter."""
    test_file = tmp_path / "test.txt"
    test_file.write_text("test")

    # Should process with matching extension
    assert should_process_file(str(test_file), file_extension=".txt")

    # Should not process with non-matching extension
    assert not should_process_file(str(test_file), file_extension=".pdf")


def test_should_process_file_names_filter(tmp_path):
    """Test should_process_file with file names filter."""
    test_file = tmp_path / "test.txt"
    test_file.write_text("test")

    # Should process with matching name
    assert should_process_file(str(test_file), file_names={"test.txt"})

    # Should not process with non-matching name
    assert not should_process_file(str(test_file), file_names={"other.txt"})


def test_should_process_file_size_filters(tmp_path):
    """Test should_process_file with size filters."""
    test_file = tmp_path / "test.txt"
    test_file.write_text("test content")

    # Test min_size filter
    assert should_process_file(str(test_file), min_size="1B")
    assert not should_process_file(str(test_file), min_size="1KB")

    # Test max_size filter
    assert should_process_file(str(test_file), max_size="1KB")
    assert not should_process_file(str(test_file), max_size="1B")


def test_should_process_file_os_error(tmp_path):
    """Test should_process_file with OSError (file not found)."""
    non_existent_file = tmp_path / "nonexistent.txt"
    assert not should_process_file(str(non_existent_file))


def test_count_files_recursive_false(tmp_path):
    """Test count_files with recursive=False."""
    # Create nested structure
    subdir = tmp_path / "subdir"
    subdir.mkdir()
    (tmp_path / "file1.txt").write_text("test")
    (subdir / "file2.txt").write_text("test")

    # Should only count files in root directory
    count = count_files(tmp_path, recursive=False, file_extension=".txt")
    assert count == 1


def test_count_files_with_filters(tmp_path):
    """Test count_files with various filters."""
    # Create test files
    (tmp_path / "test1.txt").write_text("test")
    (tmp_path / "test2.pdf").write_text("test")
    (tmp_path / "large.txt").write_text("x" * 1024)  # 1KB file

    # Test extension filter
    count = count_files(tmp_path, recursive=True, file_extension=".txt")
    assert count == 2

    # Test size filter
    count = count_files(tmp_path, recursive=True, min_size="500B")
    assert count == 1
