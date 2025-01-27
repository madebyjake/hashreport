"""Tests for config utility."""

import pytest

from hashreport.utils.config import HashReportConfig


def test_hashreport_config_defaults():
    """Test default values in HashReportConfig."""
    cfg = HashReportConfig()
    if cfg.default_algorithm != "md5":
        pytest.fail("Expected default_algorithm to be 'md5'")
    if cfg.default_format != "csv":
        pytest.fail("Expected default_format to be 'csv'")
    if not cfg.email_defaults:
        pytest.fail("Expected email_defaults to be initialized")


def test_hashreport_config_max_workers(monkeypatch):
    """Test that max_workers is set based on CPU count."""

    def mock_cpu_count():
        return 8

    monkeypatch.setattr("os.cpu_count", mock_cpu_count)
    cfg = HashReportConfig(max_workers=None)
    if cfg.max_workers != 8:
        pytest.fail("Expected max_workers to match the mock CPU count")
