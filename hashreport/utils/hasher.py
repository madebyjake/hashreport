"""Utilities for file hashing and metadata collection."""

import datetime
import hashlib
import logging
import mmap
import os
from contextlib import contextmanager
from pathlib import Path
from typing import Dict, Optional, Tuple

from hashreport.config import get_config

logger = logging.getLogger(__name__)

# Get configuration instance
config = get_config()


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
        if (
            use_mmap and file_size > 0 and file_size >= config.mmap_threshold
        ):  # Only use mmap for files over threshold
            try:
                with mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as mm:
                    yield mm
                return
            except Exception:
                # Fall back to regular file reading if mmap fails
                f.seek(0)
        yield f


def calculate_hash(
    filepath: str, algorithm: str = None
) -> Tuple[str, Optional[str], str]:
    """Calculate hash for a file."""
    algorithm = algorithm or config.default_algorithm
    try:
        hasher = hashlib.new(algorithm)

        # Use mmap for large files
        file_size = os.path.getsize(filepath)
        use_mmap = file_size > config.mmap_threshold  # e.g., 10MB

        with get_file_reader(filepath, use_mmap=use_mmap) as f:
            # For mmap objects, read directly
            if isinstance(f, mmap.mmap):
                hasher.update(f)
            else:
                # For regular files, read in chunks
                for chunk in iter(lambda: f.read(config.chunk_size), b""):
                    hasher.update(chunk)

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
