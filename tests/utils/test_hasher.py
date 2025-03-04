"""Tests for hasher utility."""

import mmap
from unittest.mock import patch

import pytest

from hashreport.utils.hasher import (
    calculate_hash,
    format_size,
    get_file_reader,
    is_file_eligible,
    show_available_options,
)


def test_calculate_hash_valid(tmp_path):
    """Test calculating hash of a valid file."""
    file_path = tmp_path / "sample.txt"
    file_path.write_text("hello world")
    result = calculate_hash(str(file_path))
    if result[1] is None:
        pytest.fail("Expected a valid hash for an existing file.")


def test_calculate_hash_nonexistent():
    """Test calculating hash for a nonexistent file."""
    result = calculate_hash("nonexistent_file.txt")
    if result[1] is not None:
        pytest.fail("Expected hash to be None for a nonexistent file.")


def test_is_file_eligible(tmp_path):
    """Test file eligibility based on size constraints."""
    file_path = tmp_path / "smallfile.txt"
    file_path.write_text("abcd")
    if not is_file_eligible(str(file_path), min_size=1, max_size=10):
        pytest.fail("File should be eligible based on the specified size constraints.")


def test_get_file_reader(tmp_path):
    """Test file reader context manager."""
    test_file = tmp_path / "test.txt"
    test_file.write_text("test content")

    with get_file_reader(str(test_file)) as reader:
        content = reader.read()
        if b"test content" not in content:
            pytest.fail("Expected to read file content")


def test_get_file_reader_empty_file(tmp_path):
    """Test reader with empty file (should not use mmap)."""
    empty_file = tmp_path / "empty.txt"
    empty_file.touch()

    with get_file_reader(str(empty_file)) as reader:
        if "mmap" in str(type(reader)):
            pytest.fail("Expected regular file reader for empty file")


def test_calculate_hash_with_algorithm(tmp_path):
    """Test hash calculation with different algorithms."""
    test_file = tmp_path / "test.txt"
    test_file.write_text("test content")

    # Test with SHA-256
    filepath, hash_value, _ = calculate_hash(str(test_file), "sha256")
    if hash_value is None:
        pytest.fail("Expected valid SHA-256 hash")
    if len(hash_value) != 64:  # SHA-256 produces 64 character hashes
        pytest.fail("Invalid SHA-256 hash length")


def test_format_size_edge_cases():
    """Test size formatting edge cases."""
    if format_size(None) is not None:
        pytest.fail("Expected None for None input")
    if format_size(0) != "0.00 MB":
        pytest.fail("Expected '0.00 MB' for zero bytes")


@patch("builtins.print")
def test_show_available_options(mock_print):
    """Test showing available hash algorithms."""
    show_available_options()
    if not mock_print.called:
        pytest.fail("Expected print to be called")


def test_get_file_reader_respects_mmap_threshold(tmp_path):
    """Test that get_file_reader respects mmap threshold configuration."""
    from hashreport.config import HashReportConfig

    # Create a test file just under the threshold
    test_file = tmp_path / "small.txt"
    test_file.write_bytes(b"x" * (HashReportConfig.mmap_threshold - 1))

    with get_file_reader(str(test_file)) as reader:
        assert not isinstance(reader, mmap.mmap), "Should not use mmap for small files"

    # Create a test file over the threshold
    large_file = tmp_path / "large.txt"
    large_file.write_bytes(b"x" * (HashReportConfig.mmap_threshold + 1))

    with get_file_reader(str(large_file)) as reader:
        assert isinstance(reader, mmap.mmap), "Should use mmap for large files"


def test_calculate_hash_with_different_sizes(tmp_path):
    """Test hash calculation with files of different sizes."""
    from hashreport.config import HashReportConfig

    # Test with small file
    small_file = tmp_path / "small.txt"
    small_file.write_bytes(b"x" * 1024)  # 1KB
    small_result = calculate_hash(str(small_file))
    assert small_result[1] is not None, "Small file hash should succeed"

    # Test with file just at threshold
    threshold_file = tmp_path / "threshold.txt"
    threshold_file.write_bytes(b"x" * HashReportConfig.mmap_threshold)
    threshold_result = calculate_hash(str(threshold_file))
    assert threshold_result[1] is not None, "Threshold file hash should succeed"
