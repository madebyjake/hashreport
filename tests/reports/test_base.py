"""Tests for the base report handler module."""

from pathlib import Path

import pytest

from hashreport.reports.base import BaseReportHandler
from hashreport.utils.exceptions import ReportError


class TestHandler:
    """Test helper class to create handler instances."""

    @staticmethod
    def create_complete():
        """Create a fully implemented test handler."""

        class CompleteHandler(BaseReportHandler):
            def read(self):
                return []

            def write(self, data, **kwargs):
                pass

            def append(self, entry):
                pass

        return CompleteHandler("test.txt")

    @staticmethod
    def create_incomplete():
        """Create an incomplete test handler."""

        class IncompleteHandler(BaseReportHandler):
            def read(self):
                pass  # Empty implementation

            def write(self, data, **kwargs):
                pass  # Empty implementation

            # Deliberately missing append method to test interface validation

        return IncompleteHandler


def test_base_handler_initialization():
    """Test initialization of a complete handler."""
    handler = TestHandler.create_complete()
    if not isinstance(handler.filepath, Path):
        pytest.fail("Expected filepath to be a Path")


def test_missing_required_methods():
    """Test that incomplete handler raises NotImplementedError."""
    with pytest.raises(NotImplementedError) as exc_info:
        TestHandler.create_incomplete()("test.txt")
    if "Handler missing required methods: append" not in str(exc_info.value):
        pytest.fail("Expected missing 'append' method in the exception message")


def test_validate_path(tmp_path):
    """Test validating path creation."""
    handler = TestHandler.create_complete()
    handler.filepath = tmp_path / "nested" / "test.txt"
    handler.validate_path()
    if not (tmp_path / "nested").exists():
        pytest.fail("Expected 'nested' directory to exist after validate_path()")


def test_validate_path_error(tmp_path, monkeypatch):
    """Test that validate_path raises ReportError on permission errors."""
    handler = TestHandler.create_complete()
    handler.filepath = tmp_path / "test.txt"

    def mock_exists(*args, **kwargs):
        return False

    def mock_mkdir(*args, **kwargs):
        raise PermissionError("Access denied")

    monkeypatch.setattr(Path, "exists", mock_exists)
    monkeypatch.setattr(Path, "mkdir", mock_mkdir)

    with pytest.raises(ReportError) as exc_info:
        handler.validate_path()
    if "Failed to create directory" not in str(exc_info.value):
        pytest.fail(
            "Expected 'Failed to create directory' text in the exception message"
        )
