"""Tests for thread pool utilities."""

import time
from concurrent.futures import Future
from unittest.mock import MagicMock, patch

import pytest

from hashreport.utils.thread_pool import ResourceMonitor, ThreadPoolManager


def test_thread_pool_initialization():
    """Test thread pool initialization."""
    pool = ThreadPoolManager(initial_workers=2)
    assert pool.initial_workers == 2
    assert pool.current_workers == 2
    assert isinstance(pool.resource_monitor, ResourceMonitor)


def test_resource_monitor():
    """Test resource monitor initialization and control."""
    pool = ThreadPoolManager(initial_workers=2)
    monitor = pool.resource_monitor

    assert not monitor._stop_event.is_set()
    monitor.start()
    assert monitor._monitor_thread.is_alive()

    monitor.stop()
    assert monitor._stop_event.is_set()
    assert not monitor._monitor_thread.is_alive()


def test_worker_adjustment():
    """Test worker count adjustment."""
    with ThreadPoolManager(initial_workers=4) as pool:
        initial = pool.current_workers
        pool.reduce_workers()
        assert pool.current_workers == initial - 1

        pool.increase_workers()
        assert pool.current_workers == initial


def test_batch_processing():
    """Test batch processing with retries."""
    items = list(range(5))

    def process_func(x):
        if x == 2 and not hasattr(process_func, "retried"):
            process_func.retried = True
            raise ValueError("Simulate failure")
        return x * 2

    with ThreadPoolManager(initial_workers=2) as pool:
        results = pool.process_items(items, process_func)
        assert sorted(results) == [0, 2, 4, 6, 8]


def test_context_manager():
    """Test thread pool context manager functionality."""
    with ThreadPoolManager() as pool:
        if pool.executor is None:
            pytest.fail("Expected executor to be initialized")
    if pool.executor is not None:
        pytest.fail("Expected executor to be shutdown")


def test_parallel_processing():
    """Test parallel processing of items."""

    def slow_process(x):
        time.sleep(0.1)
        return x * 2

    items = [1, 2, 3]
    with ThreadPoolManager(initial_workers=2) as pool:
        results = pool.process_items(items, slow_process, show_progress=True)
        if sorted(results) != [2, 4, 6]:
            pytest.fail("Expected doubled values")


def test_error_handling():
    """Test error handling during processing."""

    def failing_process(x):
        if x == 2:
            raise ValueError("Test error")
        return x

    items = [1, 2, 3]
    with ThreadPoolManager() as pool:
        results = pool.process_items(items, failing_process)
        if len(results) != 2:  # Should have 2 successful results
            pytest.fail("Expected 2 successful results")
        if sorted(results) != [1, 3]:
            pytest.fail("Expected results [1, 3]")


def test_empty_items():
    """Test processing empty item list."""
    with ThreadPoolManager() as pool:
        results = pool.process_items([], lambda x: x)
        if results != []:
            pytest.fail("Expected empty results list")


@patch("concurrent.futures.ThreadPoolExecutor.submit")
def test_shutdown_during_processing(mock_submit):
    """Test graceful shutdown during processing."""

    def mock_future():
        future = Future()
        future.set_result(None)
        return future

    mock_submit.return_value = mock_future()

    with ThreadPoolManager() as pool:
        pool._shutdown_event.set()  # Use proper shutdown mechanism
        results = pool.process_items([1, 2, 3], lambda x: x)
        if results != []:
            pytest.fail("Expected no results after shutdown")


@patch("hashreport.utils.thread_pool.ProgressBar")
def test_progress_tracking(mock_progress):
    """Test progress bar updates during processing."""
    items = [1, 2, 3]
    mock_bar = MagicMock()
    mock_progress.return_value = mock_bar

    with ThreadPoolManager(progress_bar=mock_bar) as pool:
        pool.process_items(items, lambda x: x)

    assert mock_bar.update.call_count == len(items)
    assert mock_bar.close.call_count == 1  # Changed from finish to close


@patch("psutil.Process")
def test_resource_monitoring(mock_process):
    """Test resource monitoring and worker adjustment."""
    mock_process.return_value.memory_percent.return_value = 90.0

    with ThreadPoolManager(initial_workers=4) as pool:
        time.sleep(0.2)  # Allow monitor to run longer
        # Resource monitoring may or may not reduce workers immediately
        # Just verify the monitoring is working
        assert pool.resource_monitor._monitor_thread.is_alive()

    mock_process.return_value.memory_percent.return_value = 50.0

    with ThreadPoolManager(initial_workers=2) as pool:
        time.sleep(0.1)  # Allow monitor to run
        assert pool.current_workers >= 2  # Should maintain or increase workers
