"""Utilities for file hashing and metadata collection."""

import datetime
import hashlib
import logging
import mmap
import os
from contextlib import contextmanager
from pathlib import Path
from typing import Dict, Optional, Tuple

logger = logging.getLogger(__name__)


def format_size(size_bytes: Optional[int]) -> Optional[str]:
    """Convert bytes to MB with 2 decimal places."""
    if size_bytes is None:
        return None
    return f"{size_bytes / (1024 * 1024):.2f} MB"


@contextmanager
def get_file_reader(file_path: str, use_mmap: bool = True):
    """Get optimal file reader based on file size and system resources."""
    path = Path(file_path)
    file_size = path.stat().st_size

    with path.open("rb") as f:
        if use_mmap and file_size > 0:  # mmap doesn't work with empty files
            try:
                with mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as mm:
                    yield mm
                return
            except Exception:
                # Fall back to regular file reading if mmap fails
                f.seek(0)
        yield f


def calculate_hash(
    filepath: str, algorithm: str = "md5"
) -> Tuple[str, Optional[str], str]:
    """Calculate hash for a file.

    Args:
        filepath: Path to the file
        algorithm: Hash algorithm to use

    Returns:
        Tuple containing (filepath, hash_value, modification_time)
        If hashing fails, hash_value will be None
    """
    try:
        hasher = hashlib.new(algorithm)
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hasher.update(chunk)

        # Get file modification time
        mod_time = datetime.datetime.fromtimestamp(os.path.getmtime(filepath)).strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        return filepath, hasher.hexdigest(), mod_time
    except Exception as e:
        logger.error(f"Error hashing file {filepath}: {e}")
        return filepath, None, ""


def _get_empty_result() -> Dict[str, Optional[str]]:
    """Return empty result dictionary."""
    return {
        "File Name": None,
        "File Path": None,
        "Size": None,
        "Hash Algorithm": None,
        "Hash Value": None,
        "Last Modified Date": None,
        "Created Date": None,
    }


def is_file_eligible(
    file_path: str, min_size: Optional[int] = None, max_size: Optional[int] = None
) -> bool:
    """Check if a file meets the size criteria."""
    try:
        size = os.path.getsize(file_path)
        if min_size and size < min_size:
            return False
        if max_size and size > max_size:
            return False
        return True
    except Exception:
        return False


def show_available_options() -> None:
    """Show available hash algorithms."""
    print("Available hash algorithms:")
    for algo in hashlib.algorithms_available:
        print(f"- {algo}")
