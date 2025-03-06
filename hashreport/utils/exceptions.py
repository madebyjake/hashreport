"""Custom exceptions for hashreport."""


class HashReportError(Exception):
    """Base exception for hashreport."""


class ConfigError(HashReportError):
    """Exception raised for configuration errors.

    This includes:
    - Invalid configuration files
    - Missing required settings
    - Invalid setting values
    """


class FileAccessError(HashReportError):
    """Exception raised for file access errors.

    This includes:
    - Permission denied
    - File not found
    - Path not accessible
    """


class ReportError(HashReportError):
    """Exception raised for report operation errors.

    This includes:
    - Invalid report format
    - Report generation failures
    - Report parsing errors
    """


class EmailError(HashReportError):
    """Exception raised for email-related errors.

    This includes:
    - SMTP connection failures
    - Authentication errors
    - Invalid email configuration
    - Send failures
    """


class ValidationError(HashReportError):
    """Exception raised for validation errors.

    This includes:
    - Invalid input parameters
    - Data format validation failures
    - Business rule violations
    """
