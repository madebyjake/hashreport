"""Tests for custom exceptions."""

import pytest

from hashreport.utils.exceptions import (
    ConfigError,
    EmailError,
    FileAccessError,
    HashReportError,
    ReportError,
    ValidationError,
)


def test_hashreport_error_inheritance():
    """Test that derived exceptions inherit from HashReportError."""
    if not issubclass(FileAccessError, HashReportError):
        pytest.fail("FileAccessError should inherit from HashReportError")
    if not issubclass(ReportError, HashReportError):
        pytest.fail("ReportError should inherit from HashReportError")
    if not issubclass(EmailError, HashReportError):
        pytest.fail("EmailError should inherit from HashReportError")
    if not issubclass(ValidationError, HashReportError):
        pytest.fail("ValidationError should inherit from HashReportError")
    if not issubclass(ConfigError, HashReportError):
        pytest.fail("ConfigError should inherit from HashReportError")
