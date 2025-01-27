"""Tests for thread pool utilities."""

import time
from concurrent.futures import Future
from unittest.mock import MagicMock, patch

import pytest

from hashreport.utils.thread_pool import ThreadPoolManager


def test_thread_pool_initialization():
    """Test thread pool initialization."""
    pool = ThreadPoolManager(initial_workers=2)
    if pool.initial_workers != 2:
        pytest.fail("Expected initial_workers to be 2")


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
    mock_progress.return_value.finish = MagicMock()

    with ThreadPoolManager() as pool:
        pool.process_items(items, lambda x: x)

    assert mock_progress.return_value.update.call_count == len(items)
    mock_progress.return_value.finish.assert_called_once()
    mock_progress.return_value.finish.assert_called_once()
