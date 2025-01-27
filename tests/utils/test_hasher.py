"""Tests for hasher utility."""

import pytest

from hashreport.utils.hasher import calculate_hash, is_file_eligible


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
