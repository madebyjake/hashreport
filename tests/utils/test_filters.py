"""Tests for filters utility."""

from unittest.mock import patch

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


def test_compile_patterns_case_sensitivity():
    """Test pattern compilation with case sensitivity."""
    patterns = ["Test.*"]

    # Test case insensitive (default)
    result = compile_patterns(patterns, use_regex=True)
    if not result[0].search("test.txt"):
        pytest.fail("Expected case-insensitive match")

    # Test case sensitive
    result = compile_patterns(patterns, use_regex=True, case_sensitive=True)
    if result[0].search("test.txt"):
        pytest.fail("Expected case-sensitive match to fail")


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


def test_matches_pattern_filename_only():
    """Test that pattern matching only uses filename."""
    patterns = compile_patterns(["test.*"], use_regex=True)

    # Should match regardless of path
    if not matches_pattern("/long/path/test.txt", patterns, use_regex=True):
        pytest.fail("Expected match on filename only")

    if not matches_pattern("test.txt", patterns, use_regex=True):
        pytest.fail("Expected match on filename")


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


def test_pattern_error_handling():
    """Test error handling for invalid patterns."""
    # Invalid regex pattern
    patterns = compile_patterns(["[invalid"], use_regex=True)
    assert len(patterns) == 0, "Expected empty list for invalid pattern"

    # Invalid glob pattern
    assert not matches_pattern("test.txt", ["["], use_regex=False)


def test_compile_patterns_empty():
    """Test pattern compilation with empty patterns."""
    result = compile_patterns([])
    assert result == []

    result = compile_patterns(None)
    assert result == []


def test_compile_patterns_invalid_regex():
    """Test pattern compilation with invalid regex patterns."""
    patterns = ["[invalid", "(*invalid)", "invalid*"]
    result = compile_patterns(patterns, use_regex=True)
    assert len(result) == 0


def test_matches_pattern_regex_edge_cases():
    """Test regex pattern matching edge cases."""
    # Test with empty pattern
    assert not matches_pattern("test.txt", [], use_regex=True)

    # Test with invalid regex pattern
    assert not matches_pattern("test.txt", ["[invalid"], use_regex=True)

    # Test with complex regex pattern
    patterns = compile_patterns([r"^[a-z]+\.(txt|json)$"], use_regex=True)
    assert matches_pattern("test.txt", patterns, use_regex=True)
    assert matches_pattern("data.json", patterns, use_regex=True)
    assert not matches_pattern("123.txt", patterns, use_regex=True)


def test_should_process_file_size_edge_cases(tmp_path):
    """Test file size filter edge cases."""
    test_file = tmp_path / "test.txt"
    test_file.write_text("test content")

    # Test with zero size
    assert not should_process_file(str(test_file), min_size=1000)
    assert should_process_file(str(test_file), max_size=1000)

    # Test with negative size
    assert not should_process_file(str(test_file), min_size=-1)
    assert not should_process_file(str(test_file), max_size=-1)

    # Test with equal min and max size
    file_size = test_file.stat().st_size
    assert should_process_file(str(test_file), min_size=file_size, max_size=file_size)
    assert not should_process_file(
        str(test_file), min_size=file_size + 1, max_size=file_size + 1
    )


def test_should_process_file_pattern_combinations(tmp_path):
    """Test combinations of include and exclude patterns."""
    test_file = tmp_path / "test.txt"
    test_file.write_text("test content")

    # Test with both include and exclude patterns
    assert should_process_file(
        str(test_file), include_patterns=["*.txt"], exclude_patterns=["*.tmp"]
    )

    # Test with conflicting patterns
    assert not should_process_file(
        str(test_file), include_patterns=["*.txt"], exclude_patterns=["*.txt"]
    )

    # Test with multiple patterns
    assert should_process_file(
        str(test_file), include_patterns=["*.txt", "test.*"], exclude_patterns=["*.tmp"]
    )

    # Test with regex patterns
    assert should_process_file(
        str(test_file),
        include_patterns=[r"\.txt$"],
        exclude_patterns=[r"\.tmp$"],
        use_regex=True,
    )


def test_should_process_file_error_handling(tmp_path):
    """Test error handling in file processing."""
    # Test with invalid file path
    assert not should_process_file("invalid/path/file.txt")

    # Test with permission error
    test_file = tmp_path / "test.txt"
    test_file.write_text("test content")

    with patch("pathlib.Path.stat") as mock_stat:
        mock_stat.side_effect = PermissionError("Permission denied")
        assert not should_process_file(str(test_file))

    # Test with other file system errors
    with patch("pathlib.Path.stat") as mock_stat:
        mock_stat.side_effect = OSError("File system error")
        assert not should_process_file(str(test_file))
