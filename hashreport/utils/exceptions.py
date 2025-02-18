"""Custom exceptions for hashreport."""


class HashReportError(Exception):
    """Base exception for hashreport."""

    pass


class ConfigError(HashReportError):
    """Raised when there's an error with configuration."""

    pass


class FileAccessError(HashReportError):
    """Raised when there's an error accessing a file."""

    pass


class ReportError(HashReportError):
    """Raised when there's an error with report operations."""

    pass


class EmailError(HashReportError):
    """Raised when there's an error with email operations."""

    pass


class ValidationError(HashReportError):
    """Raised when there's an error with validation."""

    pass
