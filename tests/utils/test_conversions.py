"""Tests for conversions utility."""

import pytest

from hashreport.utils.conversions import format_size, parse_size


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
