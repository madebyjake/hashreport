"""Tests for config utility."""

from pathlib import Path

import pytest

from hashreport.config import HashReportConfig, get_config


def test_hashreport_config_defaults():
    """Test default values in HashReportConfig."""
    cfg = HashReportConfig()
    assert cfg.default_algorithm == "md5", "Expected default_algorithm to be 'md5'"
    assert cfg.default_format == "csv", "Expected default_format to be 'csv'"
    assert cfg.email_defaults is not None, "Expected email_defaults to be initialized"


def test_hashreport_config_max_workers(monkeypatch):
    """Test that max_workers is set based on CPU count."""

    def mock_cpu_count():
        return 8

    monkeypatch.setattr("os.cpu_count", mock_cpu_count)
    cfg = HashReportConfig(max_workers=None)
    assert cfg.max_workers == 8, "Expected max_workers to match the mock CPU count"


def test_get_config_metadata():
    """Test that config metadata is properly loaded."""
    cfg = HashReportConfig()
    # Initialize required metadata fields
    cfg.name = "test"
    cfg.version = "0.1.0"
    cfg.description = "Test description"
    cfg.authors = ["Test Author"]
    cfg.project_license = "AGPL-3.0"
    cfg.urls = {"repository": "https://example.com"}

    metadata = cfg.get_metadata()
    assert metadata["name"] == "test"
    assert metadata["version"] == "0.1.0"
    assert metadata["description"] == "Test description"
    assert metadata["authors"] == ["Test Author"]
    assert metadata["license"] == "AGPL-3.0"
    assert metadata["urls"] == {"repository": "https://example.com"}


def test_config_from_file(tmp_path):
    """Test loading config from file."""
    config_content = """
[tool.poetry]
name = "hashreport"
version = "0.1.0"
description = "Test project"
authors = ["Test Author"]
license = "AGPL-3.0"

[tool.hashreport]
default_algorithm = "sha256"
"""
    config_file = tmp_path / "pyproject.toml"
    config_file.write_text(config_content)

    cfg = HashReportConfig.from_file(config_file)
    assert cfg.name == "hashreport"
    assert cfg.default_algorithm == "sha256"


def test_invalid_config_file(tmp_path):
    """Test handling of invalid TOML file."""
    config_file = tmp_path / "pyproject.toml"
    config_file.write_text("invalid toml content")

    with pytest.raises(ValueError):
        HashReportConfig.from_file(config_file)


def test_missing_required_metadata(tmp_path):
    """Test handling of missing required metadata."""
    config_content = """
[tool.poetry]
# Missing required name and version fields
description = "Test project"
"""
    config_file = tmp_path / "pyproject.toml"
    config_file.write_text(config_content)

    with pytest.raises(ValueError):
        HashReportConfig.from_file(config_file)


def test_load_metadata():
    """Test metadata loading from poetry config."""
    poetry_config = {
        "name": "test-project",
        "version": "1.0.0",
        "description": "Test Description",
        "authors": ["Test Author"],
        "license": "MIT",
        "urls": {"repository": "https://example.com"},
    }

    metadata = HashReportConfig._load_metadata(poetry_config)
    assert metadata["name"] == "test-project"
    assert metadata["version"] == "1.0.0"
    assert metadata["description"] == "Test Description"
    assert metadata["authors"] == ["Test Author"]
    assert metadata["project_license"] == "MIT"
    assert metadata["urls"] == {"repository": "https://example.com"}


def test_find_valid_config(tmp_path):
    """Test finding valid config in directory hierarchy."""
    nested_dir = tmp_path / "a" / "b" / "c"
    nested_dir.mkdir(parents=True)
    config_file = tmp_path / "pyproject.toml"

    config_content = """
[tool.poetry]
name = "test-project"
version = "1.0.0"
"""
    config_file.write_text(config_content)

    config = HashReportConfig._find_valid_config(nested_dir)
    assert config is not None
    assert config["tool"]["poetry"]["name"] == "test-project"


def test_get_config_singleton():
    """Test that get_config returns a singleton instance."""
    config1 = get_config()
    config2 = get_config()
    assert config1 is config2


def test_get_config_fallback():
    """Test fallback behavior when no valid config is found."""
    # Force reload of config
    import hashreport.config

    hashreport.config.loaded_config = None

    # Temporarily modify DEFAULT_CONFIG_PATH to a non-existent path
    original_path = HashReportConfig.DEFAULT_CONFIG_PATH
    HashReportConfig.DEFAULT_CONFIG_PATH = Path("nonexistent.toml")

    try:
        config = get_config()
        assert config.name == "hashreport"
        assert config.version == "0.0.0"
    finally:
        # Restore original path
        HashReportConfig.DEFAULT_CONFIG_PATH = original_path


def test_email_defaults():
    """Test email defaults configuration."""
    config = HashReportConfig()
    assert config.email_defaults["port"] == 587
    assert config.email_defaults["use_tls"] is True
    assert config.email_defaults["host"] == "localhost"


def test_custom_email_defaults():
    """Test custom email defaults."""
    custom_email = {"port": 465, "use_tls": False, "host": "smtp.example.com"}
    config = HashReportConfig(email_defaults=custom_email)
    assert config.email_defaults == custom_email
