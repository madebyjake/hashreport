"""File filtering utilities."""

import fnmatch
import logging
import re
from pathlib import Path
from typing import List, Optional, Pattern, Union


def compile_patterns(
    patterns: List[str], use_regex: bool = False
) -> List[Union[str, Pattern]]:
    """Compile file matching patterns."""
    if not patterns:
        return []

    if use_regex:
        return [re.compile(pattern) for pattern in patterns]
    return patterns


def matches_pattern(
    path: str, patterns: List[Union[str, Pattern]], use_regex: bool = False
) -> bool:
    """Check if path matches any pattern."""
    if not patterns:
        return True

    path = str(Path(path))
    for pattern in patterns:
        if use_regex:
            if isinstance(pattern, Pattern):
                if pattern.search(path):
                    return True
            else:
                if re.search(pattern, path):
                    return True
        elif fnmatch.fnmatch(path, str(pattern)):
            return True
    return False


def should_process_file(
    file_path: str,
    include_patterns: Optional[List[str]] = None,
    exclude_patterns: Optional[List[str]] = None,
    use_regex: bool = False,
    min_size: Optional[int] = None,
    max_size: Optional[int] = None,
) -> bool:
    """Determine if a file should be processed based on filters."""
    try:
        path = Path(file_path)
        if not path.is_file():
            return False

        # Check size constraints
        size = path.stat().st_size
        if min_size is not None and size < min_size:
            return False
        if max_size is not None and size > max_size:
            return False

        # Check patterns
        includes = compile_patterns(include_patterns or [], use_regex)
        excludes = compile_patterns(exclude_patterns or [], use_regex)

        if excludes and matches_pattern(file_path, excludes, use_regex):
            return False

        if includes and not matches_pattern(file_path, includes, use_regex):
            return False

        return True

    except Exception as e:
        logging.error(f"Error processing file {file_path}: {e}")
        return False
