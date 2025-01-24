"""Threading utilities for parallel processing."""

import logging
import os
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Callable, List, Optional, TypeVar

from hashreport.utils.progress_bar import ProgressBar

logger = logging.getLogger(__name__)

T = TypeVar("T")
R = TypeVar("R")


class ThreadPoolManager:
    """Thread-safe pool manager."""

    def __init__(self, initial_workers: Optional[int] = None):
        """Initialize the thread pool.

        Args:
            initial_workers: Maximum number of worker threads
        """
        self.initial_workers = initial_workers or (os.cpu_count() or 4)
        self._executor_lock = threading.Lock()
        self._executor: Optional[ThreadPoolExecutor] = None
        self._shutdown = threading.Event()

    def __enter__(self):
        """Enter the context manager.

        Returns:
            ThreadPoolManager: The thread pool instance
        """
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit the context manager and cleanup resources.

        Args:
            exc_type: Exception type if an error occurred
            exc_val: Exception value if an error occurred
            exc_tb: Exception traceback if an error occurred
        """
        self.shutdown()

    def start(self) -> None:
        """Initialize and start the thread pool."""
        with self._executor_lock:
            if self._executor is None:
                self._executor = ThreadPoolExecutor(
                    max_workers=self.initial_workers, thread_name_prefix="hashreport"
                )
                self._shutdown.clear()

    def shutdown(self) -> None:
        """Gracefully shutdown the thread pool."""
        with self._executor_lock:
            if self._executor:
                self._shutdown.set()
                self._executor.shutdown(wait=True)
                self._executor = None

    def is_shutting_down(self) -> bool:
        """Return True if the shutdown event is set."""
        return self._shutdown.is_set()

    def process_items(
        self,
        items: List[T],
        process_func: Callable[[T], R],
        desc: str = "Processing",
    ) -> List[R]:
        """Process items in parallel with progress tracking.

        Args:
            items: List of items to process
            process_func: Function to process each item
            desc: Description for the progress bar

        Returns:
            List[R]: List of results
        """
        if not items:
            logger.warning("No items to process")
            return []

        if self.is_shutting_down():
            logger.warning("Pool is shutting down, skipping new tasks.")
            return []

        results: List[R] = []
        failed_items: List[tuple[T, str]] = []
        progress = ProgressBar(total=len(items), desc=desc)

        with self:
            futures = {
                self._executor.submit(process_func, item): item for item in items
            }

            for future in as_completed(futures):
                if self._shutdown.is_set():
                    break

                item = futures[future]
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    failed_items.append((item, str(e)))
                    logger.error(f"Failed to process {item}: {e}")
                finally:
                    progress.update()

            progress.close()

        if failed_items:
            logger.warning(f"Failed to process {len(failed_items)} items")

        return results
