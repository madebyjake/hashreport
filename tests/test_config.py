"""Tests for config utility."""

from pathlib import Path
from unittest.mock import patch

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


def test_config_from_file(tmp_path):
    """Test loading config from file."""
    config_content = """
[tool.hashreport]
default_algorithm = "sha256"
"""
    config_file = tmp_path / "pyproject.toml"
    config_file.write_text(config_content)

    cfg = HashReportConfig.from_file(config_file)
    assert cfg.default_algorithm == "sha256"


def test_invalid_config_file(tmp_path):
    """Test handling of invalid TOML file."""
    config_file = tmp_path / "pyproject.toml"
    config_file.write_text("invalid toml content")

    # Should return default config instead of raising error
    cfg = HashReportConfig.from_file(config_file)
    assert isinstance(cfg, HashReportConfig)
    assert cfg.default_algorithm == "md5"  # default value


def test_find_valid_config(tmp_path):
    """Test finding valid config in directory hierarchy."""
    nested_dir = tmp_path / "a" / "b" / "c"
    nested_dir.mkdir(parents=True)
    config_file = tmp_path / "pyproject.toml"

    config_content = """
[tool.hashreport]
default_algorithm = "sha256"
"""
    config_file.write_text(config_content)

    config = HashReportConfig._find_valid_config(nested_dir)
    assert config is not None
    assert config["tool"]["hashreport"]["default_algorithm"] == "sha256"


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

    # Temporarily modify PROJECT_CONFIG_PATH to a non-existent path
    original_path = HashReportConfig.PROJECT_CONFIG_PATH
    HashReportConfig.PROJECT_CONFIG_PATH = Path("nonexistent.toml")

    try:
        config = get_config()
        assert isinstance(config, HashReportConfig)
        assert config.default_algorithm == "md5"  # default value
    finally:
        # Restore original path
        HashReportConfig.PROJECT_CONFIG_PATH = original_path


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


def test_get_settings_path():
    """Test getting settings path."""
    cfg = HashReportConfig()
    path = cfg.get_settings_path()
    assert path.name == "settings.toml"
    assert ".config/hashreport" in str(path)


def test_get_all_settings():
    """Test getting complete settings."""
    cfg = HashReportConfig()
    cfg.name = "test"
    cfg.version = "0.1.0"

    settings = cfg.get_all_settings()
    assert "email_defaults" in settings
    assert "logging" in settings
    assert "progress" in settings
    assert "reports" in settings

    # Check default sections are included
    assert settings["email_defaults"]["port"] == 587
    assert settings["email_defaults"]["host"] == "localhost"


def test_load_settings(tmp_path):
    """Test loading settings from file."""
    settings_file = tmp_path / "settings.toml"
    settings_content = """
    [hashreport]
    default_algorithm = "sha256"
    """
    settings_file.write_text(settings_content)

    with patch("hashreport.config.HashReportConfig.SETTINGS_PATH", settings_file):
        cfg = HashReportConfig()
        settings = cfg.load_settings()
        assert settings.get("default_algorithm") == "sha256"
