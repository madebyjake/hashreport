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
        if use_regex:
            if isinstance(pattern, Pattern):
                try:
                    if pattern.search(filename):
                        return True
                except (re.error, TypeError) as e:
                    logging.warning(f"Error matching pattern '{pattern}': {e}")
            else:
                try:
                    flags = 0 if case_sensitive else re.IGNORECASE
                    if re.search(pattern, filename, flags):
                        return True
                except re.error as e:
                    logging.warning(f"Invalid regex pattern '{pattern}': {e}")
        else:
            try:
                if fnmatch.fnmatch(filename, str(pattern)):
                    return True
            except Exception as e:
                logging.warning(f"Error matching glob pattern '{pattern}': {e}")

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
        if min_size is not None and (min_size < 0 or size < min_size):
            return False
        if max_size is not None and (max_size < 0 or size > max_size):
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
