"""Tests for the ProgressBar utility."""

import threading
import time
from unittest.mock import patch

from tqdm import tqdm

from hashreport.utils.progress_bar import ProgressBar, create_progress_bar


def test_progress_bar_init():
    """Test creating a ProgressBar instance."""
    pbar = ProgressBar(total=5, desc="Testing")
    assert pbar._bar.total == 5
    assert pbar._bar.desc == "Testing"
    assert isinstance(pbar._bar, tqdm)


def test_progress_bar_update():
    """Test updating the progress bar."""
    pbar = ProgressBar(total=2)
    pbar.update()
    pbar.update()
    assert pbar._bar.n == 2


def test_progress_bar_finish():
    """Test finishing the progress bar."""
    pbar = ProgressBar(total=3)
    with patch.object(pbar._bar, "close") as mock_close:
        pbar.finish()
        mock_close.assert_called_once()


def test_thread_safety():
    """Test thread-safe updates to progress bar."""
    pbar = ProgressBar(total=1000)
    threads = []

    def update_progress():
        for _ in range(100):
            pbar.update()
            time.sleep(0.001)

    # Create 10 threads that each update 100 times
    for _ in range(10):
        t = threading.Thread(target=update_progress)
        threads.append(t)
        t.start()

    # Wait for all threads to complete
    for t in threads:
        t.join()

    assert pbar._bar.n == 1000


def test_create_progress_bar():
    """Test the create_progress_bar utility function."""
    bar = create_progress_bar(total=10, desc="Test")
    assert isinstance(bar, tqdm)
    assert bar.total == 10
    assert bar.desc == "Test"
    bar.close()
