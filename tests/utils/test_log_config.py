"""Tests for logging configuration utility."""

import logging

from hashreport.utils.log_config import setup_logging


def test_debug_logging_level():
    """Test that debug=True sets logger level to DEBUG."""
    setup_logging(debug=True)
    logger = logging.getLogger("hashreport")
    assert (
        logger.level == logging.DEBUG
    ), "Expected logger level to be DEBUG when debug=True"


def test_specified_logging_level():
    """Test that specifying a level overrides default."""
    setup_logging(level=logging.WARNING, debug=False)
    logger = logging.getLogger("hashreport")
    assert logger.level == logging.WARNING, "Expected logger level to be WARNING"
