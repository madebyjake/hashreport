"""Type definitions and validation utilities for hashreport."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import (
    Any,
    Dict,
    List,
    Literal,
    NewType,
    Optional,
    Protocol,
    TypeVar,
    Union,
    runtime_checkable,
)

logger = logging.getLogger(__name__)

# Type aliases for better readability and consistency
FilePath = Union[str, Path]
FileSize = int  # Size in bytes
HashAlgorithm = Literal["md5", "sha1", "sha256", "sha512", "blake2b"]
ReportFormat = Literal["csv", "json"]
EmailAddress = NewType("EmailAddress", str)
Hostname = NewType("Hostname", str)
PortNumber = NewType("PortNumber", int)

# Generic type variables
T = TypeVar("T")
K = TypeVar("K")
V = TypeVar("V")

# Report entry structure
ReportEntry = Dict[str, Union[str, int, float, None]]
ReportData = List[ReportEntry]

# Configuration types
ConfigDict = Dict[str, Any]
EmailConfig = Dict[str, Union[str, int, bool]]

# Performance metrics
PerformanceSummary = Dict[str, Union[int, float, str]]


@runtime_checkable
class Hashable(Protocol):
    """Protocol for objects that can be hashed."""

    def __hash__(self) -> int:
        """Return hash value."""
        ...


@runtime_checkable
class FileProcessor(Protocol[T]):
    """Protocol for file processing functions."""

    def __call__(self, filepath: FilePath) -> T:
        """Process a file and return result."""
        ...


@runtime_checkable
class ReportHandler(Protocol):
    """Protocol for report handlers."""

    def read(self) -> ReportData:
        """Read report data."""
        ...

    def write(self, data: ReportData, **kwargs: Any) -> None:
        """Write report data."""
        ...

    def append(self, entry: ReportEntry) -> None:
        """Append single entry."""
        ...


def validate_file_path(path: Any) -> FilePath:
    """Validate and convert to FilePath type.

    Args:
        path: Path-like object to validate

    Returns:
        Validated FilePath

    Raises:
        ValueError: If path is invalid
    """
    if isinstance(path, (str, Path)):
        return path
    raise ValueError(f"Invalid file path type: {type(path)}")


def validate_hash_algorithm(algorithm: str) -> HashAlgorithm:
    """Validate hash algorithm string.

    Args:
        algorithm: Algorithm name to validate

    Returns:
        Validated HashAlgorithm

    Raises:
        ValueError: If algorithm is not supported
    """
    valid_algorithms: List[HashAlgorithm] = [
        "md5",
        "sha1",
        "sha256",
        "sha512",
        "blake2b",
    ]
    if algorithm.lower() in valid_algorithms:
        return algorithm.lower()  # type: ignore
    raise ValueError(f"Unsupported hash algorithm: {algorithm}")


def validate_report_format(format_str: str) -> ReportFormat:
    """Validate report format string.

    Args:
        format_str: Format string to validate

    Returns:
        Validated ReportFormat

    Raises:
        ValueError: If format is not supported
    """
    valid_formats: List[ReportFormat] = ["csv", "json"]
    if format_str.lower() in valid_formats:
        return format_str.lower()  # type: ignore
    raise ValueError(f"Unsupported report format: {format_str}")


def validate_email_address(email: str) -> EmailAddress:
    """Validate email address format.

    Args:
        email: Email address to validate

    Returns:
        Validated EmailAddress

    Raises:
        ValueError: If email format is invalid
    """
    import re

    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    if re.match(pattern, email):
        return EmailAddress(email)
    raise ValueError(f"Invalid email address format: {email}")


def validate_port_number(port: int) -> PortNumber:
    """Validate port number.

    Args:
        port: Port number to validate

    Returns:
        Validated PortNumber

    Raises:
        ValueError: If port is invalid
    """
    if 1 <= port <= 65535:
        return PortNumber(port)
    raise ValueError(f"Invalid port number: {port}")


def validate_hostname(hostname: str) -> Hostname:
    """Validate hostname format.

    Args:
        hostname: Hostname to validate

    Returns:
        Validated Hostname

    Raises:
        ValueError: If hostname format is invalid
    """
    import re

    # More strict pattern that requires at least one dot and proper TLD
    pattern = (
        r"^[a-zA-Z0-9]([a-zA-Z0-9-]*[a-zA-Z0-9])?"
        r"(\.[a-zA-Z0-9]([a-zA-Z0-9-]*[a-zA-Z0-9])?)*\.[a-zA-Z]{2,}$"
    )
    if re.match(pattern, hostname):
        return Hostname(hostname)
    raise ValueError(f"Invalid hostname format: {hostname}")


def is_valid_report_entry(entry: Any) -> bool:
    """Permissive: Accept any dict as a valid report entry."""
    return isinstance(entry, dict)


def validate_report_data(data: Any) -> ReportData:
    """Permissive: Accept any list of dicts as valid report data."""
    if not isinstance(data, list):
        raise ValueError("Report data must be a list")
    for i, entry in enumerate(data):
        if not is_valid_report_entry(entry):
            raise ValueError(f"Invalid report entry at index {i}: {entry}")
    return data


def safe_cast(
    value: Any, target_type: type[T], default: Optional[T] = None
) -> Optional[T]:
    """Safely cast value to target type.

    Args:
        value: Value to cast
        target_type: Target type
        default: Default value if casting fails

    Returns:
        Cast value or default
    """
    try:
        if isinstance(value, target_type):
            return value
        return target_type(value)
    except (ValueError, TypeError):
        logger.warning(f"Failed to cast {value} to {target_type}")
        return default


def ensure_list(value: Union[T, List[T]]) -> List[T]:
    """Ensure value is a list.

    Args:
        value: Value that might be a single item or list

    Returns:
        List containing the value(s)
    """
    if isinstance(value, list):
        return value
    return [value]


def ensure_dict(value: Any) -> Dict[str, Any]:
    """Ensure value is a dictionary.

    Args:
        value: Value to ensure is a dict

    Returns:
        Dictionary value

    Raises:
        ValueError: If value cannot be converted to dict
    """
    if isinstance(value, dict):
        return value
    if hasattr(value, "__dict__"):
        return value.__dict__
    raise ValueError(f"Cannot convert {type(value)} to dict")
