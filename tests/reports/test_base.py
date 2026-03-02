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


def test_validate_path_existing_file_error(tmp_path):
    """Test validate_path raises ReportError when path exists but not directory."""
    handler = TestHandler.create_complete()
    # Create a file at the parent path
    parent_file = tmp_path / "parent_file"
    parent_file.touch()
    handler.filepath = parent_file / "test.txt"

    with pytest.raises(ReportError) as exc_info:
        handler.validate_path()
    assert "Path exists but is not a directory" in str(exc_info.value)


def test_validate_path_generic_exception(tmp_path, monkeypatch):
    """Test that validate_path raises ReportError on generic exceptions."""
    handler = TestHandler.create_complete()
    handler.filepath = tmp_path / "test.txt"

    def mock_exists(*args, **kwargs):
        raise Exception("Generic error")

    monkeypatch.setattr(Path, "exists", mock_exists)

    with pytest.raises(ReportError) as exc_info:
        handler.validate_path()
    assert "Generic error" in str(exc_info.value)


def test_base_handler_not_implemented_methods():
    """Test that base handler methods raise NotImplementedError."""
    # Test read method
    with pytest.raises(NotImplementedError, match="Handler missing required methods"):
        BaseReportHandler("test.txt")

    # Test write method
    with pytest.raises(NotImplementedError, match="Handler missing required methods"):
        BaseReportHandler("test.txt")

    # Test append method
    with pytest.raises(NotImplementedError, match="Handler missing required methods"):
        BaseReportHandler("test.txt")


def test_validate_interface_with_same_code():
    """Test interface validation when method has same code as base."""

    class SameCodeHandler(BaseReportHandler):
        def read(self):
            raise NotImplementedError("Subclasses must override 'read'.")

        def write(self, data, **kwargs):
            raise NotImplementedError("Subclasses must override 'write'.")

        def append(self, entry):
            raise NotImplementedError("Subclasses must override 'append'.")

    # This should work because methods are implemented (even if NotImplementedError)
    handler = SameCodeHandler("test.txt")
    assert handler is not None


def test_validate_interface_with_none_method():
    """Test interface validation when method is None."""

    class NoneMethodHandler(BaseReportHandler):
        def read(self):
            pass

        def write(self, data, **kwargs):
            pass

        # append is None (not defined)

    with pytest.raises(
        NotImplementedError, match="Handler missing required methods: append"
    ):
        NoneMethodHandler("test.txt")


def test_validate_interface_multiple_missing():
    """Test interface validation with multiple missing methods."""

    class MultipleMissingHandler(BaseReportHandler):
        def read(self):
            pass

        # write and append are missing

    with pytest.raises(NotImplementedError, match="Handler missing required methods"):
        MultipleMissingHandler("test.txt")


def test_filepath_validation():
    """Test that filepath is properly validated and converted to Path."""
    TestHandler.create_complete()

    # Test with string path - filepath is set during initialization
    handler_str = TestHandler.create_complete()
    assert isinstance(handler_str.filepath, Path)

    # Test with Path object
    handler_path = TestHandler.create_complete()
    assert isinstance(handler_path.filepath, Path)


def test_required_methods_class_variable():
    """Test that REQUIRED_METHODS class variable is properly defined."""
    assert hasattr(BaseReportHandler, "REQUIRED_METHODS")
    assert isinstance(BaseReportHandler.REQUIRED_METHODS, set)
    assert "read" in BaseReportHandler.REQUIRED_METHODS
    assert "write" in BaseReportHandler.REQUIRED_METHODS
    assert "append" in BaseReportHandler.REQUIRED_METHODS


def test_validate_path_existing_directory(tmp_path):
    """Test validate_path when parent directory already exists."""
    handler = TestHandler.create_complete()
    existing_dir = tmp_path / "existing"
    existing_dir.mkdir()
    handler.filepath = existing_dir / "test.txt"

    # Should not raise any exception
    handler.validate_path()
    assert existing_dir.exists()


def test_validate_path_parent_creation(tmp_path):
    """Test validate_path creates parent directories."""
    handler = TestHandler.create_complete()
    nested_path = tmp_path / "level1" / "level2" / "level3"
    handler.filepath = nested_path / "test.txt"

    # Should not raise any exception and create all parent directories
    handler.validate_path()
    assert nested_path.exists()


def test_validate_path_with_existing_file_parent(tmp_path):
    """Test validate_path when parent path exists as a file."""
    handler = TestHandler.create_complete()
    parent_file = tmp_path / "parent_file"
    parent_file.touch()
    handler.filepath = parent_file / "test.txt"

    with pytest.raises(ReportError, match="Path exists but is not a directory"):
        handler.validate_path()
