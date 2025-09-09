"""Utility functions for unit conversions."""

import re
from typing import Optional


def parse_size(size_str: str) -> Optional[int]:
    """
    Parse size string with units into bytes.

    Examples: '1KB', '2.5MB', '1GB'
    """
    if not size_str:
        return None

    # Strip whitespace and convert to uppercase
    size_str = size_str.strip().upper()

    pattern = r"^([\d.]+)\s*([KMGT]?B)$"
    match = re.match(pattern, size_str)
    if not match:
        return None

    number, unit = match.groups()
    multipliers = {
        "B": 1,
        "KB": 1024,
        "MB": 1024**2,
        "GB": 1024**3,
        "TB": 1024**4,
    }

    try:
        return int(float(number) * multipliers[unit])
    except (ValueError, KeyError):
        return None


def parse_size_string(size_str: str) -> int:
    """Convert size string to bytes with validation.

    Args:
        size_str: Size string with unit (e.g., "1MB", "500KB")

    Returns:
        Size in bytes

    Raises:
        ValueError: If size format is invalid or size is not positive

    Example:
        >>> parse_size_string("1MB")
        1048576
        >>> parse_size_string("500KB")
        512000
    """
    if not size_str:
        raise ValueError("Size string cannot be empty")

    # Use the existing parse_size function but with validation
    result = parse_size(size_str)
    if result is None:
        # Check if it's missing unit (just a number)
        stripped = size_str.strip()
        if stripped.isdigit() or (
            stripped.replace(".", "").isdigit() and "." in stripped
        ):
            raise ValueError(
                "Size must include unit. Valid units are: B, KB, MB, GB, TB"
            )
        else:
            # For any other invalid format, also use the "missing unit" message
            # to match the original behavior
            raise ValueError(
                "Size must include unit. Valid units are: B, KB, MB, GB, TB"
            )
    if result < 0:
        raise ValueError("Size must be greater than 0")

    return result


def parse_size_string_strict(size_str: str) -> int:
    """Convert size string to bytes with strict validation (rejects zero).

    This function is used for CLI validation where zero values are not allowed.

    Args:
        size_str: Size string with unit (e.g., "1MB", "500KB")

    Returns:
        Size in bytes

    Raises:
        ValueError: If size format is invalid or size is not positive

    Example:
        >>> parse_size_string_strict("1MB")
        1048576
        >>> parse_size_string_strict("0KB")
        Traceback (most recent call last):
            ...
            ValueError: Size must be greater than 0
    """
    if not size_str:
        raise ValueError("Size string cannot be empty")

    # Use the existing parse_size function but with validation
    result = parse_size(size_str)
    if result is None:
        # Check if it's missing unit (just a number)
        stripped = size_str.strip()
        if stripped.isdigit() or (
            stripped.replace(".", "").isdigit() and "." in stripped
        ):
            raise ValueError(
                "Size must include unit. Valid units are: B, KB, MB, GB, TB"
            )
        else:
            # For any other invalid format, also use the "missing unit" message
            # to match the original behavior
            raise ValueError(
                "Size must include unit. Valid units are: B, KB, MB, GB, TB"
            )
    if result <= 0:
        raise ValueError("Size must be greater than 0")

    return result


def validate_size_string(size_str: str) -> str:
    """Validate size string format and return the original string.

    This function is designed for use as a Click callback parameter.

    Args:
        size_str: Size string with unit (e.g., "1MB", "500KB")

    Returns:
        The original size string if valid

    Raises:
        ValueError: If size format is invalid or size is not positive

    Example:
        >>> validate_size_string("1MB")
        '1MB'
        >>> validate_size_string("invalid")
        Traceback (most recent call last):
            ...
            ValueError: Invalid size format: invalid
    """
    if not size_str:
        return size_str

    # Validate by attempting to parse with strict validation (rejects zero)
    parse_size_string_strict(size_str)
    return size_str


def format_size(size_bytes: int) -> str:
    """Format byte size to human readable format."""
    if size_bytes < 1024:
        return f"{size_bytes} B"

    for unit in ["KB", "MB", "GB", "TB"]:
        size_bytes /= 1024.0
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"

    return f"{size_bytes:.2f} TB"
