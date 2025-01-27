"""Tests for the ProgressBar utility."""

import pytest

from hashreport.utils.progress_bar import ProgressBar


def test_progress_bar_init():
    """Test creating a ProgressBar instance."""
    pbar = ProgressBar(total=5, desc="Testing")
    if pbar._bar.total != 5:
        pytest.fail("Expected total to be 5")


def test_progress_bar_update():
    """Test updating the progress bar."""
    pbar = ProgressBar(total=2)
    pbar.update()
    pbar.update()
    if pbar._bar.n != 2:
        pytest.fail("Expected progress bar count to be 2 after two updates")


def test_progress_bar_finish():
    """Test finishing the progress bar."""
    pbar = ProgressBar(total=3)
    pbar.finish()
    # TQDM doesn't expose a "finished" state easily; just ensure no error raised
