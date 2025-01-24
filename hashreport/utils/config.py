"""Configuration management for hashreport."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class HashReportConfig:
    """Configuration settings for hashreport."""

    default_algorithm: str = "md5"
    chunk_size: int = 4096
    max_workers: Optional[int] = None
    default_format: str = "csv"
    timestamp_format: str = "%Y-%m-%d %H:%M:%S"
    email_defaults: dict = None

    def __post_init__(self):
        """Initialize default values."""
        if self.email_defaults is None:
            self.email_defaults = {"port": 587, "use_tls": True, "host": "localhost"}
        if self.max_workers is None:
            import os

            self.max_workers = os.cpu_count() or 4


config = HashReportConfig()
