"""Tests for config utility."""

from hashreport.config import HashReportConfig


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
    cfg.project_license = "MIT"  # Change here
    cfg.urls = {"repository": "https://example.com"}

    metadata = cfg.get_metadata()
    assert metadata["name"] == "test"
    assert metadata["version"] == "0.1.0"
    assert metadata["description"] == "Test description"
    assert metadata["authors"] == ["Test Author"]
    assert metadata["license"] == "MIT"  # This stays as license in metadata output
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
