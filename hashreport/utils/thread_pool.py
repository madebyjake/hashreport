"""Thread pool management utilities."""

import logging
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Callable, Iterable, List, Optional

import psutil

from hashreport.config import get_config
from hashreport.utils.progress_bar import ProgressBar

logger = logging.getLogger(__name__)
config = get_config()


class ResourceMonitor:
    """Monitor system resources and adjust thread pool size."""

    def __init__(self, pool_manager: "ThreadPoolManager") -> None:
        """Initialize resource monitor.

        Args:
            pool_manager: ThreadPoolManager instance to monitor
        """
        self.pool_manager = pool_manager
        self._stop_event = threading.Event()
        self._monitor_thread = threading.Thread(
            target=self._monitor_resources, daemon=True
        )

    def start(self):
        """Start resource monitoring."""
        self._monitor_thread.start()

    def stop(self):
        """Stop resource monitoring."""
        self._stop_event.set()
        self._monitor_thread.join()

    def _monitor_resources(self):
        """Monitor system resources and adjust thread count."""
        while not self._stop_event.is_set():
            try:
                memory_percent = psutil.Process().memory_percent()
                if memory_percent > config.memory_threshold:
                    self.pool_manager.reduce_workers()
                elif memory_percent < config.memory_threshold * 0.8:  # 20% headroom
                    self.pool_manager.increase_workers()
            except Exception as e:
                logger.error(f"Resource monitoring error: {e}")
            time.sleep(config.resource_check_interval)


class ThreadPoolManager:
    """Manages thread pool execution with progress tracking and resource monitoring."""

    def __init__(
        self,
        initial_workers: Optional[int] = None,
        progress_bar: Optional[ProgressBar] = None,
    ) -> None:
        """Initialize thread pool manager.

        Args:
            initial_workers: Number of worker threads to use, defaults to config value
            progress_bar: Optional progress bar for tracking operations
        """
        self.initial_workers = initial_workers or config.max_workers
        self.current_workers = self.initial_workers
        self.executor = None
        self._shutdown_event = threading.Event()
        self.progress_bar = progress_bar
        self.resource_monitor = ResourceMonitor(self)
        self._worker_lock = threading.Lock()

    def __enter__(self):
        """Initialize thread pool on context entry."""
        self.executor = ThreadPoolExecutor(max_workers=self.initial_workers)
        self._shutdown_event.clear()
        self.resource_monitor.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Clean up resources on context exit."""
        self._shutdown_event.set()
        self.resource_monitor.stop()
        if self.progress_bar:
            self.progress_bar.close()
        if self.executor:
            self.executor.shutdown(wait=True)
            self.executor = None

    def adjust_workers(self, new_count: int):
        """Adjust the number of worker threads."""
        with self._worker_lock:
            if config.min_workers <= new_count <= config.max_workers:
                self.current_workers = new_count
                if self.executor:
                    self.executor._max_workers = new_count

    def reduce_workers(self):
        """Reduce the number of worker threads."""
        self.adjust_workers(max(config.min_workers, self.current_workers - 1))

    def increase_workers(self):
        """Increase the number of worker threads."""
        self.adjust_workers(min(config.max_workers, self.current_workers + 1))

    def process_batch(
        self, batch: List[Any], process_func: Callable, retries: int = 0
    ) -> List[Any]:
        """Process a batch of items with retry logic."""
        if not batch:
            return []

        futures = []
        results = []
        retry_items = []

        for item in batch:
            if self._shutdown_event.is_set():
                break
            future = self.executor.submit(process_func, item)
            futures.append((future, item))

        for future, item in futures:
            if self._shutdown_event.is_set():
                break
            try:
                result = future.result()
                results.append(result)
                if self.progress_bar:
                    self.progress_bar.update()
            except Exception as e:
                logger.error(f"Error processing item: {e}")
                retry_items.append(item)
                if self.progress_bar:
                    self.progress_bar.update()

        # Handle retries if needed
        if retry_items and retries < config.max_retries:
            time.sleep(config.retry_delay)
            retry_results = self.process_batch(retry_items, process_func, retries + 1)
            results.extend(retry_results)

        return results

    def process_items(
        self,
        items: Iterable[Any],
        process_func: Callable,
        **kwargs,
    ) -> List[Any]:
        """Process items in batches with resource monitoring."""
        if self._shutdown_event.is_set() or not self.executor:
            return []

        all_results = []
        current_batch = []

        for item in items:
            if self._shutdown_event.is_set():
                break

            current_batch.append(item)

            if len(current_batch) >= config.batch_size:
                results = self.process_batch(current_batch, process_func)
                all_results.extend(results)
                current_batch = []

        # Process remaining items
        if current_batch and not self._shutdown_event.is_set():
            results = self.process_batch(current_batch, process_func)
            all_results.extend(results)

        return all_results
