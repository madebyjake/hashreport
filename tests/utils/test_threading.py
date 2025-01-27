"""Tests for threading utilities."""

import time
from concurrent.futures import Future
from unittest.mock import MagicMock, patch

import pytest

from hashreport.utils.threading import ThreadPoolManager


def test_thread_pool_initialization():
    """Test thread pool initialization."""
    pool = ThreadPoolManager(initial_workers=2)
    if pool.initial_workers != 2:
        pytest.fail("Expected initial_workers to be 2")


def test_context_manager():
    """Test thread pool context manager functionality."""
    with ThreadPoolManager() as pool:
        if pool._executor is None:
            pytest.fail("Expected executor to be initialized")
    if pool._executor is not None:
        pytest.fail("Expected executor to be shutdown")


def test_parallel_processing():
    """Test parallel processing of items."""

    def slow_process(x):
        time.sleep(0.1)
        return x * 2

    items = [1, 2, 3]
    with ThreadPoolManager(initial_workers=2) as pool:
        results = pool.process_items(items, slow_process, desc="Testing")
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
        pool._shutdown.set()  # Simulate shutdown signal
        results = pool.process_items([1, 2, 3], lambda x: x)
        if results != []:
            pytest.fail("Expected no results after shutdown signal")


def test_progress_tracking():
    """Test progress bar updates during processing."""
    items = [1, 2, 3]
    mock_progress = MagicMock()

    with patch("hashreport.utils.threading.ProgressBar", return_value=mock_progress):
        with ThreadPoolManager() as pool:
            pool.process_items(items, lambda x: x)

        if mock_progress.update.call_count != len(items):
            pytest.fail(f"Expected {len(items)} progress updates")
        mock_progress.close.assert_called_once()
