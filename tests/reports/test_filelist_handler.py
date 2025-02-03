"""Tests for the filelist handler."""

from unittest.mock import patch

from hashreport.reports.filelist_handler import (
    get_filelist_filename,
    list_files_in_directory,
)


def test_get_filelist_filename(tmp_path):
    """Test generating a filelist filename with timestamp."""
    dir_path = tmp_path
    filename = get_filelist_filename(str(dir_path))
    assert filename.startswith(str(dir_path))
    assert "filelist_" in filename
    assert filename.endswith(".txt")


@patch("hashreport.reports.filelist_handler.os.walk")
@patch("hashreport.reports.filelist_handler.count_files", return_value=2)
def test_list_files_in_directory(mock_count_files, mock_oswalk, tmp_path):
    """Test listing files in a directory."""
    # Create test files
    test_file1 = tmp_path / "file1.txt"
    test_file2 = tmp_path / "file2.txt"
    test_file1.touch()
    test_file2.touch()

    mock_oswalk.return_value = [
        (str(tmp_path), [], ["file1.txt", "file2.txt"]),
    ]

    output_file = tmp_path / "filelist.txt"
    list_files_in_directory(str(tmp_path), str(output_file))

    assert output_file.exists()
    with output_file.open("r", encoding="utf-8") as f:
        lines = f.readlines()
        assert len(lines) == 2
        assert str(test_file1) in lines[0]
        assert str(test_file2) in lines[1]
