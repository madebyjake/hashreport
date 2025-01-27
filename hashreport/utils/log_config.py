"""Logging configuration for hashreport."""

import logging
from typing import Optional


def setup_logging(level: Optional[int] = None, debug: bool = False) -> None:
    """Set up logging configuration.

    Args:
        level: Optional logging level. Defaults to INFO if not specified.
        debug: Enable debug logging
    """
    if debug:
        level = logging.DEBUG
    elif level is None:
        level = logging.INFO

    logger = logging.getLogger("hashreport")
    logger.setLevel(level)

    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    # Enable debug logging for specific modules
    if debug:
        logging.getLogger("hashreport.utils.scanner").setLevel(logging.DEBUG)
        logging.getLogger("hashreport.reports").setLevel(logging.DEBUG)
