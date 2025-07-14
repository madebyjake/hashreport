"""Thread pool management utilities."""

import logging
import os
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from typing import Any, Callable, Iterable, List, Optional

import psutil

from hashreport.config import get_config
from hashreport.utils.progress_bar import ProgressBar
from hashreport.utils.type_defs import PerformanceSummary

logger = logging.getLogger(__name__)
config = get_config()


@dataclass
class PerformanceMetrics:
    """Performance metrics for thread pool operations."""

    total_items_processed: int = 0
    successful_items: int = 0
    failed_items: int = 0
    retry_count: int = 0
    total_processing_time: float = 0.0
    average_processing_time: float = 0.0
    worker_adjustments: int = 0
    memory_usage_samples: List[float] = field(default_factory=list)
    cpu_usage_samples: List[float] = field(default_factory=list)
    start_time: Optional[float] = None
    end_time: Optional[float] = None

    def start_timing(self) -> None:
        """Start performance timing."""
        self.start_time = time.time()

    def end_timing(self) -> None:
        """End performance timing."""
        self.end_time = time.time()
        if self.start_time:
            self.total_processing_time = self.end_time - self.start_time

    def update_average_processing_time(self, item_time: float) -> None:
        """Update average processing time."""
        if self.total_items_processed > 0:
            self.average_processing_time = (
                self.average_processing_time * (self.total_items_processed - 1)
                + item_time
            ) / self.total_items_processed
        else:
            self.average_processing_time = item_time

    def get_summary(self) -> PerformanceSummary:
        """Get performance summary."""
        return {
            "total_items": self.total_items_processed,
            "successful": self.successful_items,
            "failed": self.failed_items,
            "retries": self.retry_count,
            "total_time": self.total_processing_time,
            "avg_time_per_item": self.average_processing_time,
            "worker_adjustments": self.worker_adjustments,
            "success_rate": (
                self.successful_items / self.total_items_processed * 100
                if self.total_items_processed > 0
                else 0
            ),
            "avg_memory_usage": (
                sum(self.memory_usage_samples) / len(self.memory_usage_samples)
                if self.memory_usage_samples
                else 0
            ),
            "avg_cpu_usage": (
                sum(self.cpu_usage_samples) / len(self.cpu_usage_samples)
                if self.cpu_usage_samples
                else 0
            ),
        }


class ResourceMonitor:
    """Monitor system resources and adjust thread pool size with adaptive scaling."""

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
        self._last_adjustment_time = 0
        self._adjustment_cooldown = 5.0  # Minimum seconds between adjustments
        self._consecutive_reductions = 0
        self._consecutive_increases = 0
        self._max_consecutive_adjustments = 3

    def start(self) -> None:
        """Start resource monitoring."""
        self._monitor_thread.start()

    def stop(self) -> None:
        """Stop resource monitoring."""
        self._stop_event.set()
        self._monitor_thread.join()

    def _monitor_resources(self) -> None:
        """Monitor system resources and adjust thread count with adaptive logic."""
        while not self._stop_event.is_set():
            try:
                current_time = time.time()

                # Get system metrics
                memory_percent = psutil.Process().memory_percent()
                cpu_percent = psutil.cpu_percent(interval=0.1)

                # Store metrics for performance tracking
                self.pool_manager.metrics.memory_usage_samples.append(memory_percent)
                self.pool_manager.metrics.cpu_usage_samples.append(cpu_percent)

                # Keep only recent samples (last 100)
                if len(self.pool_manager.metrics.memory_usage_samples) > 100:
                    self.pool_manager.metrics.memory_usage_samples.pop(0)
                if len(self.pool_manager.metrics.cpu_usage_samples) > 100:
                    self.pool_manager.metrics.cpu_usage_samples.pop(0)

                # Check if enough time has passed since last adjustment
                if (
                    current_time - self._last_adjustment_time
                    < self._adjustment_cooldown
                ):
                    time.sleep(config.resource_check_interval)
                    continue

                # Adaptive worker adjustment based on resource usage
                should_adjust = self._should_adjust_workers(memory_percent, cpu_percent)

                if should_adjust == "reduce":
                    if self._consecutive_reductions < self._max_consecutive_adjustments:
                        self.pool_manager.reduce_workers()
                        self._consecutive_reductions += 1
                        self._consecutive_increases = 0
                        self._last_adjustment_time = current_time
                        self.pool_manager.metrics.worker_adjustments += 1
                        logger.debug(
                            f"Reduced workers to {self.pool_manager.current_workers} "
                            f"(memory: {memory_percent:.1f}%, "
                            f"cpu: {cpu_percent:.1f}%)"
                        )
                elif should_adjust == "increase":
                    if self._consecutive_increases < self._max_consecutive_adjustments:
                        self.pool_manager.increase_workers()
                        self._consecutive_increases += 1
                        self._consecutive_reductions = 0
                        self._last_adjustment_time = current_time
                        self.pool_manager.metrics.worker_adjustments += 1
                        logger.debug(
                            f"Increased workers to {self.pool_manager.current_workers} "
                            f"(memory: {memory_percent:.1f}%, "
                            f"cpu: {cpu_percent:.1f}%)"
                        )
                else:
                    # Reset consecutive counters if no adjustment needed
                    self._consecutive_reductions = 0
                    self._consecutive_increases = 0

            except Exception as e:
                logger.error(f"Resource monitoring error: {e}")
            time.sleep(config.resource_check_interval)

    def _should_adjust_workers(
        self, memory_percent: float, cpu_percent: float
    ) -> Optional[str]:
        """Determine if workers should be adjusted based on resource usage.

        Returns:
            "reduce", "increase", or None
        """
        # High memory pressure - reduce workers
        if memory_percent > config.memory_threshold:
            return "reduce"

        # High CPU pressure - reduce workers if memory is also high
        if cpu_percent > 80 and memory_percent > config.memory_threshold * 0.7:
            return "reduce"

        # Low resource usage - increase workers if we have headroom
        if (
            memory_percent < config.memory_threshold * 0.6
            and cpu_percent < 60
            and self.pool_manager.current_workers < self.pool_manager.max_workers
        ):
            return "increase"

        return None


class ThreadPoolManager:
    """Manages thread pool execution with adaptive scaling and performance monitoring."""  # noqa: E501

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
        self.max_workers = config.max_workers
        self.min_workers = config.min_workers
        self.executor: Optional[ThreadPoolExecutor] = None
        self._shutdown_event = threading.Event()
        self.progress_bar = progress_bar
        self.resource_monitor = ResourceMonitor(self)
        self._worker_lock = threading.Lock()
        self.metrics = PerformanceMetrics()
        self._backpressure_threshold = 0.8  # Queue utilization threshold
        self._queue_size = 0
        self._max_queue_size = 0
        self._submitted_futures: List[Any] = []

    def __enter__(self) -> "ThreadPoolManager":
        """Initialize thread pool on context entry."""
        self.executor = ThreadPoolExecutor(max_workers=self.initial_workers)
        self._shutdown_event.clear()
        self.resource_monitor.start()
        self.metrics.start_timing()
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Clean up resources on context exit."""
        self._shutdown_event.set()
        self.resource_monitor.stop()
        self.metrics.end_timing()
        if self.progress_bar:
            self.progress_bar.close()
        if self.executor:
            self.executor.shutdown(wait=True)
            self.executor = None
        # Clear futures tracking
        self._submitted_futures.clear()

    def adjust_workers(self, new_count: int) -> None:
        """Adjust the number of worker threads."""
        with self._worker_lock:
            if self.min_workers <= new_count <= self.max_workers:
                old_count = self.current_workers
                self.current_workers = new_count
                logger.debug(f"Adjusted workers from {old_count} to {new_count}")

    def reduce_workers(self) -> None:
        """Reduce the number of worker threads."""
        self.adjust_workers(max(self.min_workers, self.current_workers - 1))

    def increase_workers(self) -> None:
        """Increase the number of worker threads."""
        self.adjust_workers(min(self.max_workers, self.current_workers + 1))

    def _check_backpressure(self) -> bool:
        """Check if backpressure should be applied due to high queue utilization."""
        if not self.executor:
            return False

        try:
            # Count pending futures (submitted but not completed)
            pending_futures = len([f for f in self._submitted_futures if not f.done()])
            self._queue_size = pending_futures
            self._max_queue_size = max(self._max_queue_size, pending_futures)

            # Apply backpressure if too many pending tasks
            if pending_futures > self.current_workers * self._backpressure_threshold:
                logger.debug(f"Backpressure applied: pending futures {pending_futures}")
                return True
        except Exception as e:
            logger.debug(f"Could not check backpressure: {e}")
            # Fallback: assume no backpressure needed
            self._queue_size = 0

        return False

    def process_batch(
        self, batch: List[Any], process_func: Callable, retries: int = 0
    ) -> List[Any]:
        """Process a batch of items with retry logic and backpressure."""
        if not batch:
            return []

        futures = []
        results = []
        retry_items = []
        batch_start_time = time.time()

        # Check for backpressure before submitting new work
        if self._check_backpressure():
            time.sleep(0.1)  # Brief pause to allow queue to drain

        for item in batch:
            if self._shutdown_event.is_set():
                break
            future = self.executor.submit(process_func, item)
            futures.append((future, item))
            self._submitted_futures.append(future)

        for future, item in futures:
            if self._shutdown_event.is_set():
                break
            try:
                item_start_time = time.time()
                result = future.result()
                item_time = time.time() - item_start_time

                results.append(result)
                self.metrics.total_items_processed += 1
                self.metrics.successful_items += 1
                self.metrics.update_average_processing_time(item_time)

                if self.progress_bar:
                    file_name = os.path.basename(item) if isinstance(item, str) else ""
                    self.progress_bar.update(1, file_name=file_name)

            except Exception as e:
                logger.error(f"Error processing item: {e}")
                retry_items.append(item)
                self.metrics.failed_items += 1
                if self.progress_bar:
                    self.progress_bar.update(1)
            finally:
                # Remove completed futures from tracking list
                if future in self._submitted_futures:
                    self._submitted_futures.remove(future)

        # Handle retries if needed
        if retry_items and retries < config.max_retries:
            self.metrics.retry_count += 1
            time.sleep(config.retry_delay)
            retry_results = self.process_batch(retry_items, process_func, retries + 1)
            results.extend(retry_results)

        batch_time = time.time() - batch_start_time
        logger.debug(f"Processed batch of {len(batch)} items in {batch_time:.2f}s")

        return results

    def process_items(
        self,
        items: Iterable[Any],
        process_func: Callable,
        **kwargs: Any,
    ) -> List[Any]:
        """Process items in batches with adaptive resource monitoring."""
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

    def get_performance_summary(self) -> PerformanceSummary:
        """Get comprehensive performance summary."""
        summary = self.metrics.get_summary()
        summary.update(
            {
                "current_workers": self.current_workers,
                "max_queue_size": self._max_queue_size,
                "current_queue_size": self._queue_size,
                "items_per_second": (
                    self.metrics.total_items_processed
                    / self.metrics.total_processing_time
                    if self.metrics.total_processing_time > 0
                    else 0
                ),
            }
        )
        return summary
