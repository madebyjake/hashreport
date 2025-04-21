"""Progress bar implementation for tracking file processing."""

import time
from threading import Lock
from typing import Optional

from tqdm import tqdm


class ProgressBar:
    """Progress bar for tracking file processing."""

    def __init__(
        self, total: int = 0, desc: str = "Processing", show_file_names: bool = False
    ):
        """Initialize the progress bar."""
        self._lock = Lock()
        self._start_time = time.time()
        self._processed = 0
        self._show_file_names = show_file_names
        self._current_file = ""

        # Customize bar format based on show_file_names setting
        bar_format = (
            "{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}]"
        )
        if show_file_names:
            bar_format = "{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}] - {postfix}"  # noqa: E501

        self._bar = tqdm(
            total=total,
            desc=desc,
            unit="files",
            unit_scale=True,
            miniters=1,
            bar_format=bar_format,
        )
        self.pbar: Optional[tqdm] = None

    def update(self, n: int = 1, file_name: str = "") -> None:
        """Update progress by n steps."""
        with self._lock:
            if self._show_file_names and file_name:
                self._current_file = file_name
                self._bar.set_postfix_str(file_name)
            self._bar.update(n)

    def finish(self) -> None:
        """Complete and close the progress bar."""
        self.close()

    def close(self) -> None:
        """Close the progress bar."""
        with self._lock:
            self._bar.close()


def create_progress_bar(
    total: int, desc: str = "Processing", show_file_names: bool = False
) -> tqdm:
    """Create a TQDM progress bar with default settings."""
    return tqdm(total=total, desc=desc, unit="files")
