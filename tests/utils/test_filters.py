"""Tests for filters utility."""

import pytest

from hashreport.utils.filters import (
    compile_patterns,
    matches_pattern,
    should_process_file,
)


def test_compile_patterns():
    """Test pattern compilation."""
    # Test glob patterns
    glob_patterns = ["*.txt", "test.*"]
    result = compile_patterns(glob_patterns)
    if not isinstance(result, list) or len(result) != 2:
        pytest.fail("Expected list of 2 glob patterns")

    # Test regex patterns
    regex_patterns = [r"\.txt$", r"^test\."]
    result = compile_patterns(regex_patterns, use_regex=True)
    if not all(hasattr(p, "search") for p in result):
        pytest.fail("Expected compiled regex patterns")


def test_matches_pattern():
    """Test pattern matching functionality."""
    # Test glob matching
    patterns = ["*.txt", "test.*"]
    if not matches_pattern("test.txt", patterns):
        pytest.fail("Expected 'test.txt' to match glob patterns")
    if matches_pattern("test.jpg", ["*.txt"]):
        pytest.fail("Expected 'test.jpg' not to match '*.txt'")

    # Test regex matching
    patterns = compile_patterns([r"\.txt$", r"^test\."], use_regex=True)
    if not matches_pattern("test.txt", patterns, use_regex=True):
        pytest.fail("Expected 'test.txt' to match regex patterns")


def test_should_process_file(tmp_path):
    """Test file processing criteria."""
    # Create test files
    test_file = tmp_path / "test.txt"
    test_file.write_text("test content")

    # Test size filters
    if not should_process_file(str(test_file), min_size=1):
        pytest.fail("File should meet minimum size requirement")
    if should_process_file(str(test_file), max_size=1):
        pytest.fail("File should not meet maximum size requirement")

    # Test patterns
    if not should_process_file(str(test_file), include_patterns=["*.txt"]):
        pytest.fail("File should match include pattern")
    if should_process_file(str(test_file), exclude_patterns=["*.txt"]):
        pytest.fail("File should match exclude pattern")

    # Test regex patterns
    if not should_process_file(
        str(test_file), include_patterns=[r"\.txt$"], use_regex=True
    ):
        pytest.fail("File should match regex pattern")


def test_should_process_invalid_file(tmp_path):
    """Test processing criteria for invalid files."""
    nonexistent = tmp_path / "nonexistent.txt"
    if should_process_file(str(nonexistent)):
        pytest.fail("Should return False for nonexistent file")

    # Create directory instead of file
    test_dir = tmp_path / "test_dir"
    test_dir.mkdir()
    if should_process_file(str(test_dir)):
        pytest.fail("Should return False for directory")
