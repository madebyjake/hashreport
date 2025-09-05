"""File filtering utilities."""

import fnmatch
import logging
import re
from pathlib import Path
from typing import List, Optional, Pattern, Union


def compile_patterns(
    patterns: List[str],
    use_regex: bool = False,
    case_sensitive: bool = False,
) -> List[Union[str, Pattern]]:
    """Compile file matching patterns."""
    if not patterns:
        return []

    if use_regex:
        flags = 0 if case_sensitive else re.IGNORECASE
        # Add multiline for matching start/end of lines
        flags |= re.MULTILINE
        # Add verbose flag for cleaner pattern formatting
        flags |= re.VERBOSE
        try:
            return [re.compile(p, flags) for p in patterns]
        except re.error as e:
            logging.error(f"Invalid regex pattern in patterns: {e}")
            return []
    return patterns


def _match_regex_pattern(
    filename: str, pattern: Union[str, Pattern], case_sensitive: bool = False
) -> bool:
    """Match a single regex pattern against filename."""
    try:
        if isinstance(pattern, Pattern):
            return bool(pattern.search(filename))
        else:
            flags = 0 if case_sensitive else re.IGNORECASE
            return bool(re.search(pattern, filename, flags))
    except (re.error, TypeError) as e:
        logging.warning(f"Error matching regex pattern '{pattern}': {e}")
        return False


def _match_glob_pattern(filename: str, pattern: str) -> bool:
    """Match a single glob pattern against filename."""
    try:
        return fnmatch.fnmatch(filename, pattern)
    except Exception as e:
        logging.warning(f"Error matching glob pattern '{pattern}': {e}")
        return False


def _match_single_pattern(
    filename: str,
    pattern: Union[str, Pattern],
    use_regex: bool = False,
    case_sensitive: bool = False,
) -> bool:
    """Match a single pattern against filename."""
    if use_regex:
        return _match_regex_pattern(filename, pattern, case_sensitive)
    else:
        return _match_glob_pattern(filename, str(pattern))


def matches_pattern(
    path: str,
    patterns: List[Union[str, Pattern]],
    use_regex: bool = False,
    case_sensitive: bool = False,
) -> bool:
    """Check if path matches any pattern."""
    if not patterns:
        return False

    # Only match against filename
    filename = Path(path).name

    for pattern in patterns:
        if _match_single_pattern(filename, pattern, use_regex, case_sensitive):
            return True

    return False


def _validate_file_basic(file_path: str) -> bool:
    """Validate basic file properties."""
    try:
        path = Path(file_path)
        return path.is_file()
    except Exception as e:
        logging.error(f"Error validating file {file_path}: {e}")
        return False


def _validate_file_size(
    file_path: str, min_size: Optional[int] = None, max_size: Optional[int] = None
) -> bool:
    """Validate file size constraints."""
    try:
        size = Path(file_path).stat().st_size

        if min_size is not None and (min_size < 0 or size < min_size):
            return False
        if max_size is not None and (max_size < 0 or size > max_size):
            return False

        return True
    except Exception as e:
        logging.error(f"Error validating file size for {file_path}: {e}")
        return False


def _validate_include_patterns(
    file_path: str,
    include_patterns: Optional[List[str]] = None,
    use_regex: bool = False,
) -> bool:
    """Validate include patterns."""
    if not include_patterns:
        return True

    includes = compile_patterns(include_patterns, use_regex)
    return matches_pattern(file_path, includes, use_regex)


def _validate_exclude_patterns(
    file_path: str,
    exclude_patterns: Optional[List[str]] = None,
    use_regex: bool = False,
) -> bool:
    """Validate exclude patterns."""
    if not exclude_patterns:
        return True

    excludes = compile_patterns(exclude_patterns, use_regex)
    return not matches_pattern(file_path, excludes, use_regex)


def should_process_file(
    file_path: str,
    include_patterns: Optional[List[str]] = None,
    exclude_patterns: Optional[List[str]] = None,
    use_regex: bool = False,
    min_size: Optional[int] = None,
    max_size: Optional[int] = None,
) -> bool:
    """Determine if a file should be processed based on filters."""
    # Basic file validation
    if not _validate_file_basic(file_path):
        return False

    # Size validation
    if not _validate_file_size(file_path, min_size, max_size):
        return False

    # Exclude patterns validation
    if not _validate_exclude_patterns(file_path, exclude_patterns, use_regex):
        return False

    # Include patterns validation
    if not _validate_include_patterns(file_path, include_patterns, use_regex):
        return False

    return True
