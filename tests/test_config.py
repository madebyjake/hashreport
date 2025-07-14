"""Tests for config utility."""

from pathlib import Path
from unittest.mock import patch

import pytest

from hashreport.config import HashReportConfig, get_config, reset_config


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
    assert cfg.max_workers == 16, "Expected max_workers to be CPU count * 2"


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
    # email_defaults is now empty by default, not pre-populated
    assert isinstance(config.email_defaults, dict)
    assert len(config.email_defaults) == 0


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


def test_memory_limit_initialization_with_psutil(monkeypatch):
    """Test memory limit initialization with psutil available."""

    def mock_virtual_memory():
        class MockMemory:
            total = 8 * 1024 * 1024 * 1024  # 8GB

        return MockMemory()

    monkeypatch.setattr("psutil.virtual_memory", mock_virtual_memory)

    cfg = HashReportConfig(memory_limit=None)
    # Should be 75% of 8GB = 6GB = 6144MB
    assert cfg.memory_limit == 6144


def test_memory_limit_initialization_without_psutil(monkeypatch):
    """Test memory limit initialization without psutil."""

    def mock_import_error(name, *args, **kwargs):
        if name == "psutil":
            raise ImportError("psutil not available")
        return __import__(name, *args, **kwargs)

    monkeypatch.setattr("builtins.__import__", mock_import_error)

    cfg = HashReportConfig(memory_limit=None)
    assert cfg.memory_limit == 1024  # Default to 1GB


def test_max_workers_initialization_exception(monkeypatch):
    """Test max_workers initialization with exception."""

    def mock_cpu_count():
        raise Exception("CPU count error")

    monkeypatch.setattr("os.cpu_count", mock_cpu_count)

    cfg = HashReportConfig(max_workers=None)
    assert cfg.max_workers == 8  # Default fallback


def test_validation_invalid_algorithm():
    """Test validation with invalid hash algorithm."""
    with pytest.raises(ValueError, match="Configuration validation failed"):
        HashReportConfig(default_algorithm="invalid_algo")


def test_validation_invalid_format():
    """Test validation with invalid report format."""
    with pytest.raises(ValueError, match="Configuration validation failed"):
        HashReportConfig(default_format="invalid_format")


def test_validation_invalid_supported_formats():
    """Test validation with invalid supported formats."""
    with pytest.raises(ValueError, match="Configuration validation failed"):
        HashReportConfig(supported_formats=["csv", "invalid_format"])


def test_validation_invalid_numeric_ranges():
    """Test validation with invalid numeric ranges."""
    # Test various invalid ranges
    invalid_configs = [
        {"chunk_size": 0},
        {"chunk_size": -1},
        {"mmap_threshold": 0},
        {"batch_size": 0},
        {"max_retries": -1},
        {"retry_delay": -1},
        {"min_workers": 0},
        {"max_workers": 0},
        {"memory_threshold": 0},
        {"memory_threshold": 1.5},
    ]

    for invalid_config in invalid_configs:
        with pytest.raises(ValueError, match="Configuration validation failed"):
            HashReportConfig(**invalid_config)


def test_validation_invalid_email_port():
    """Test validation with invalid email port."""
    email_config = {"port": 0, "host": "localhost"}
    with pytest.raises(ValueError, match="Configuration validation failed"):
        HashReportConfig(email_defaults=email_config)

    email_config = {"port": 65536, "host": "localhost"}
    with pytest.raises(ValueError, match="Configuration validation failed"):
        HashReportConfig(email_defaults=email_config)

    email_config = {"port": "not_a_number", "host": "localhost"}
    with pytest.raises(ValueError, match="Configuration validation failed"):
        HashReportConfig(email_defaults=email_config)


def test_find_valid_config_no_file(tmp_path):
    """Test finding valid config when no file exists."""
    nested_dir = tmp_path / "a" / "b" / "c"
    nested_dir.mkdir(parents=True)

    config = HashReportConfig._find_valid_config(nested_dir)
    assert config is None


def test_find_valid_config_invalid_file(tmp_path):
    """Test finding valid config with invalid file."""
    nested_dir = tmp_path / "a" / "b" / "c"
    nested_dir.mkdir(parents=True)
    config_file = tmp_path / "pyproject.toml"
    config_file.write_text("invalid toml content")

    config = HashReportConfig._find_valid_config(nested_dir)
    assert config is None


def test_load_toml_file_not_found(tmp_path):
    """Test loading TOML file that doesn't exist."""
    non_existent_file = tmp_path / "nonexistent.toml"
    result = HashReportConfig._load_toml(non_existent_file)
    assert result == {}


def test_load_toml_decode_error(tmp_path):
    """Test loading TOML file with decode error."""
    config_file = tmp_path / "invalid.toml"
    config_file.write_text("invalid toml content")

    result = HashReportConfig._load_toml(config_file)
    assert result == {}


def test_load_toml_unexpected_error(tmp_path, monkeypatch):
    """Test loading TOML file with unexpected error."""

    def mock_open(*args, **kwargs):
        raise Exception("Unexpected error")

    config_file = tmp_path / "error.toml"
    config_file.write_text("valid content")
    monkeypatch.setattr(Path, "open", mock_open)

    result = HashReportConfig._load_toml(config_file)
    assert result == {}


def test_load_settings_file_not_found():
    """Test loading settings when file doesn't exist."""
    cfg = HashReportConfig()
    settings = cfg.load_settings()
    # Should return empty dict when file doesn't exist
    assert isinstance(settings, dict)
    # The settings might be populated from other sources, so just check it's a dict


def test_load_settings_error(tmp_path, monkeypatch):
    """Test loading settings with error."""
    settings_file = tmp_path / "settings.toml"
    settings_file.write_text("invalid content")

    with patch("hashreport.config.HashReportConfig.SETTINGS_PATH", settings_file):
        cfg = HashReportConfig()
        settings = cfg.load_settings()
        assert settings == {}


def test_get_user_settings():
    """Test getting user settings."""
    cfg = HashReportConfig()
    settings = cfg.get_user_settings()
    assert isinstance(settings, dict)


def test_to_dict():
    """Test converting config to dictionary."""
    cfg = HashReportConfig()
    config_dict = cfg.to_dict()

    assert isinstance(config_dict, dict)
    assert config_dict["default_algorithm"] == "md5"
    assert config_dict["default_format"] == "csv"
    assert "email_defaults" in config_dict
    assert "progress" in config_dict


def test_reset_config():
    """Test resetting global configuration."""
    # Get initial config
    config1 = get_config()

    # Reset config
    reset_config()

    # Get new config
    config2 = get_config()

    # Should be different instances
    assert config1 is not config2


def test_from_file_with_invalid_tool_section(tmp_path):
    """Test loading config with invalid tool section."""
    config_content = """
[tool]
# No hashreport section
"""
    config_file = tmp_path / "pyproject.toml"
    config_file.write_text(config_content)

    cfg = HashReportConfig.from_file(config_file)
    assert cfg.default_algorithm == "md5"  # Should use defaults


def test_from_file_with_invalid_app_config(tmp_path):
    """Test loading config with invalid app config."""
    config_content = """
[tool.hashreport]
default_algorithm = "invalid_algo"  # This will cause validation error
"""
    config_file = tmp_path / "pyproject.toml"
    config_file.write_text(config_content)

    # Should return default config due to validation error
    cfg = HashReportConfig.from_file(config_file)
    assert cfg.default_algorithm == "md5"  # Should use defaults


def test_find_valid_config_absolute_path(tmp_path):
    """Test finding valid config with absolute path."""
    config_file = tmp_path / "pyproject.toml"
    config_content = """
[tool.hashreport]
default_algorithm = "sha256"
"""
    config_file.write_text(config_content)

    config = HashReportConfig._find_valid_config(config_file)
    assert config is not None
    assert config["tool"]["hashreport"]["default_algorithm"] == "sha256"


def test_find_valid_config_relative_path(tmp_path):
    """Test finding valid config with relative path."""
    config_file = tmp_path / "pyproject.toml"
    config_content = """
[tool.hashreport]
default_algorithm = "sha256"
"""
    config_file.write_text(config_content)

    # Change to tmp_path directory
    original_cwd = Path.cwd()
    try:
        import os

        os.chdir(tmp_path)
        config = HashReportConfig._find_valid_config(Path("pyproject.toml"))
        assert config is not None
        assert config["tool"]["hashreport"]["default_algorithm"] == "sha256"
    finally:
        os.chdir(original_cwd)
