"""Tests for conversions utility."""

import pytest

from hashreport.utils.conversions import (
    format_size,
    parse_size,
    parse_size_string,
    parse_size_string_strict,
    validate_size_string,
)


def test_parse_size():
    """Test parsing various size strings."""
    if parse_size("1KB") != 1024:
        pytest.fail("1KB should be 1024 bytes")
    if parse_size("2.5MB") != 2621440:
        pytest.fail("2.5MB should be 2621440 bytes")
    if parse_size("1GB") != 1073741824:
        pytest.fail("1GB should be 1073741824 bytes")
    if parse_size("") is not None:
        pytest.fail("Empty string should return None")


def test_format_size():
    """Test formatting byte sizes."""
    if format_size(512) != "512 B":
        pytest.fail("512 bytes should match '512 B'")
    if format_size(1024) != "1.00 KB":
        pytest.fail("1024 bytes should be '1.00 KB'")
    if format_size(1048576) != "1.00 MB":
        pytest.fail("1048576 bytes should be '1.00 MB'")


def test_parse_size_string():
    """Test parse_size_string function."""
    # Valid cases
    assert parse_size_string("1KB") == 1024
    assert parse_size_string("2.5MB") == 2621440
    assert parse_size_string("1GB") == 1073741824

    # Invalid cases that should raise ValueError
    with pytest.raises(ValueError, match="Size string cannot be empty"):
        parse_size_string("")

    with pytest.raises(ValueError, match="Size must include unit"):
        parse_size_string("123")

    with pytest.raises(ValueError, match="Size must include unit"):
        parse_size_string("abc")

    # Zero size should work (not strict)
    assert parse_size_string("0KB") == 0

    with pytest.raises(ValueError, match="Size must include unit"):
        parse_size_string("-1KB")


def test_parse_size_string_strict():
    """Test parse_size_string_strict function."""
    # Valid cases
    assert parse_size_string_strict("1KB") == 1024
    assert parse_size_string_strict("2.5MB") == 2621440
    assert parse_size_string_strict("1GB") == 1073741824

    # Invalid cases that should raise ValueError
    with pytest.raises(ValueError, match="Size string cannot be empty"):
        parse_size_string_strict("")

    with pytest.raises(ValueError, match="Size must include unit"):
        parse_size_string_strict("123")

    with pytest.raises(ValueError, match="Size must include unit"):
        parse_size_string_strict("abc")

    with pytest.raises(ValueError, match="Size must be greater than 0"):
        parse_size_string_strict("0KB")

    with pytest.raises(ValueError, match="Size must include unit"):
        parse_size_string_strict("-1KB")


def test_validate_size_string():
    """Test validate_size_string function."""
    # Valid cases - function returns the original string
    assert validate_size_string("1KB") == "1KB"
    assert validate_size_string("2.5MB") == "2.5MB"
    assert validate_size_string("1GB") == "1GB"

    # Empty string returns empty string (no validation)
    assert validate_size_string("") == ""

    # Invalid cases that should raise ValueError
    with pytest.raises(ValueError, match="Size must include unit"):
        validate_size_string("123")

    with pytest.raises(ValueError, match="Size must include unit"):
        validate_size_string("abc")

    with pytest.raises(ValueError, match="Size must be greater than 0"):
        validate_size_string("0KB")

    with pytest.raises(ValueError, match="Size must include unit"):
        validate_size_string("-1KB")


def test_parse_size_edge_cases():
    """Test parse_size with edge cases."""
    # Test None input
    assert parse_size(None) is None

    # Test empty string
    assert parse_size("") is None

    # Test whitespace
    assert parse_size("   ") is None

    # Test invalid format
    assert parse_size("invalid") is None

    # Test number without unit
    assert parse_size("123") is None

    # Test zero
    assert parse_size("0KB") == 0

    # Test negative - parse_size doesn't handle negative numbers
    assert parse_size("-1KB") is None


def test_format_size_edge_cases():
    """Test format_size with edge cases."""
    # Test zero
    assert format_size(0) == "0 B"

    # Test very small numbers
    assert format_size(1) == "1 B"
    assert format_size(999) == "999 B"

    # Test very large numbers
    assert format_size(1024**4) == "1.00 TB"  # 1 TB

    # Test fractional results
    assert format_size(1536) == "1.50 KB"  # 1.5 KB
    assert format_size(2560) == "2.50 KB"  # 2.5 KB


def test_parse_size_string_edge_cases():
    """Test parse_size_string with edge cases."""
    # Test decimal numbers
    assert parse_size_string("1.5KB") == 1536
    assert parse_size_string("2.5MB") == 2621440

    # Test very large numbers
    assert parse_size_string("999GB") == 999 * 1024**3

    # Test case sensitivity
    assert parse_size_string("1kb") == 1024
    assert parse_size_string("1Kb") == 1024
    assert parse_size_string("1KB") == 1024


def test_parse_size_string_strict_edge_cases():
    """Test parse_size_string_strict with edge cases."""
    # Test decimal numbers
    assert parse_size_string_strict("1.5KB") == 1536
    assert parse_size_string_strict("2.5MB") == 2621440

    # Test very large numbers
    assert parse_size_string_strict("999GB") == 999 * 1024**3

    # Test case sensitivity
    assert parse_size_string_strict("1kb") == 1024
    assert parse_size_string_strict("1Kb") == 1024
    assert parse_size_string_strict("1KB") == 1024


def test_validate_size_string_edge_cases():
    """Test validate_size_string with edge cases."""
    # Test decimal numbers - function returns original string
    assert validate_size_string("1.5KB") == "1.5KB"
    assert validate_size_string("2.5MB") == "2.5MB"

    # Test very large numbers
    assert validate_size_string("999GB") == "999GB"

    # Test case sensitivity
    assert validate_size_string("1kb") == "1kb"
    assert validate_size_string("1Kb") == "1Kb"
    assert validate_size_string("1KB") == "1KB"


def test_parse_size_string_error_messages():
    """Test parse_size_string error messages."""
    # Test empty string error
    with pytest.raises(ValueError) as exc_info:
        parse_size_string("")
    assert "Size string cannot be empty" in str(exc_info.value)

    # Test missing unit error for pure number
    with pytest.raises(ValueError) as exc_info:
        parse_size_string("123")
    assert "Size must include unit" in str(exc_info.value)

    # Test missing unit error for decimal number
    with pytest.raises(ValueError) as exc_info:
        parse_size_string("123.45")
    assert "Size must include unit" in str(exc_info.value)

    # Test invalid format error
    with pytest.raises(ValueError) as exc_info:
        parse_size_string("abc")
    assert "Size must include unit" in str(exc_info.value)

    # Test zero size - should work for non-strict function
    assert parse_size_string("0KB") == 0

    # Test negative size error
    with pytest.raises(ValueError) as exc_info:
        parse_size_string("-1KB")
    assert "Size must include unit" in str(exc_info.value)


def test_parse_size_string_strict_error_messages():
    """Test parse_size_string_strict error messages."""
    # Test empty string error
    with pytest.raises(ValueError) as exc_info:
        parse_size_string_strict("")
    assert "Size string cannot be empty" in str(exc_info.value)

    # Test missing unit error for pure number
    with pytest.raises(ValueError) as exc_info:
        parse_size_string_strict("123")
    assert "Size must include unit" in str(exc_info.value)

    # Test missing unit error for decimal number
    with pytest.raises(ValueError) as exc_info:
        parse_size_string_strict("123.45")
    assert "Size must include unit" in str(exc_info.value)

    # Test invalid format error
    with pytest.raises(ValueError) as exc_info:
        parse_size_string_strict("abc")
    assert "Size must include unit" in str(exc_info.value)

    # Test zero size error
    with pytest.raises(ValueError) as exc_info:
        parse_size_string_strict("0KB")
    assert "Size must be greater than 0" in str(exc_info.value)

    # Test negative size error
    with pytest.raises(ValueError) as exc_info:
        parse_size_string_strict("-1KB")
    assert "Size must include unit" in str(exc_info.value)


def test_validate_size_string_error_messages():
    """Test validate_size_string error messages."""
    # Empty string returns empty string (no error)
    assert validate_size_string("") == ""

    # Test missing unit error for pure number
    with pytest.raises(ValueError) as exc_info:
        validate_size_string("123")
    assert "Size must include unit" in str(exc_info.value)

    # Test missing unit error for decimal number
    with pytest.raises(ValueError) as exc_info:
        validate_size_string("123.45")
    assert "Size must include unit" in str(exc_info.value)

    # Test invalid format error
    with pytest.raises(ValueError) as exc_info:
        validate_size_string("abc")
    assert "Size must include unit" in str(exc_info.value)

    # Test zero size error
    with pytest.raises(ValueError) as exc_info:
        validate_size_string("0KB")
    assert "Size must be greater than 0" in str(exc_info.value)

    # Test negative size error
    with pytest.raises(ValueError) as exc_info:
        validate_size_string("-1KB")
    assert "Size must include unit" in str(exc_info.value)
