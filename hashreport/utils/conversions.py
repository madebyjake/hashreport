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

    pattern = r"^([\d.]+)\s*([KMGT]?B)$"
    match = re.match(pattern, size_str.upper())
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


def format_size(size_bytes: int) -> str:
    """Format byte size to human readable format."""
    if size_bytes < 1024:
        return f"{size_bytes} B"

    for unit in ["KB", "MB", "GB", "TB"]:
        size_bytes /= 1024.0
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"

    return f"{size_bytes:.2f} TB"
