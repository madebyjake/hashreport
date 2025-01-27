"""Thread pool management utilities."""

import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Callable, Iterable, List, Optional

from hashreport.utils.progress_bar import ProgressBar


class ThreadPoolManager:
    """Manages thread pool execution with progress tracking."""

    def __init__(
        self,
        initial_workers: Optional[int] = None,
        progress_bar: Optional[ProgressBar] = None,
    ):
        """Initialize thread pool manager.

        Args:
            initial_workers: Number of worker threads to use
            progress_bar: Optional progress bar to update
        """
        self.initial_workers = initial_workers
        self.executor = None
        self._shutdown_event = threading.Event()
        self.progress_bar = progress_bar

    def __enter__(self):
        """Initialize thread pool on context entry."""
        self.executor = ThreadPoolExecutor(max_workers=self.initial_workers)
        self._shutdown_event.clear()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Clean up resources on context exit."""
        self._shutdown_event.set()
        if self.executor:
            self.executor.shutdown(wait=True)
            self.executor = None

    def process_items(
        self,
        items: Iterable[Any],
        process_func: Callable,
        **kwargs,
    ) -> List[Any]:
        """Process items in parallel."""
        if self._shutdown_event.is_set() or not self.executor:
            return []  # Return empty list if already shutdown

        items_list = list(items)
        futures = []
        results = []

        try:
            for item in items_list:
                if self._shutdown_event.is_set():
                    break
                future = self.executor.submit(process_func, item)
                futures.append(future)

            for future in as_completed(futures):
                if self._shutdown_event.is_set():
                    break
                try:
                    result = future.result()
                    results.append(result)
                    if self.progress_bar:
                        self.progress_bar.update()
                except Exception as e:
                    if self.progress_bar:
                        self.progress_bar.update()
                    print(f"Error processing item: {e}")

        finally:
            if self.progress_bar:
                self.progress_bar.finish()

        return results
