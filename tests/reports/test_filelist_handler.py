"""Tests for the filelist handler."""

from unittest.mock import patch

from hashreport.reports.filelist_handler import (
    get_filelist_filename,
    list_files_in_directory,
)


def test_get_filelist_filename(tmp_path):
    """Test generating a filelist filename."""
    dir_path = tmp_path
    filename = get_filelist_filename(str(dir_path))
    assert filename.startswith(str(dir_path))
    assert "filelist" in filename
    assert filename.endswith(".txt")


@patch("hashreport.reports.filelist_handler.collect_files_to_list")
def test_list_files_in_directory(mock_collect, tmp_path):
    """Test listing files in a directory."""
    test_file1 = tmp_path / "file1.txt"
    test_file2 = tmp_path / "file2.txt"
    mock_collect.return_value = [str(test_file1), str(test_file2)]

    output_file = tmp_path / "filelist.txt"
    list_files_in_directory(str(tmp_path), str(output_file))

    mock_collect.assert_called_once_with(
        str(tmp_path),
        recursive=True,
        limit=None,
        include=None,
        exclude=None,
        regex=False,
        min_size=None,
        max_size=None,
    )
    assert output_file.exists()
    with output_file.open("r", encoding="utf-8") as f:
        lines = f.readlines()
        assert len(lines) == 2
        assert str(test_file1) in lines[0]
        assert str(test_file2) in lines[1]


@patch("hashreport.reports.filelist_handler.collect_files_to_list")
def test_list_files_in_directory_with_filters(mock_collect, tmp_path):
    """Test filelist with include, exclude, and limit."""
    mock_collect.return_value = [str(tmp_path / "a.txt")]
    output_file = tmp_path / "out.txt"
    list_files_in_directory(
        str(tmp_path),
        str(output_file),
        recursive=False,
        include=("*.txt",),
        exclude=("*.tmp",),
        limit=10,
    )
    mock_collect.assert_called_once_with(
        str(tmp_path),
        recursive=False,
        limit=10,
        include=("*.txt",),
        exclude=("*.tmp",),
        regex=False,
        min_size=None,
        max_size=None,
    )
