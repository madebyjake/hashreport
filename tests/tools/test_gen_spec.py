"""Test module for the gen_spec tool."""

import tempfile
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from tools.gen_spec import (
    format_build_requires,
    format_changelog_entries,
    format_dependencies,
    parse_changelog,
)


@pytest.fixture
def mock_config():
    """Create a mock configuration object for testing."""
    config_mock = MagicMock()
    metadata = {
        "name": "hashreport",
        "version": "1.0.0",
        "description": "Generate detailed file hash reports",
        "license": "AGPLv3",
        "authors": ["Test Author <test@example.com>"],
        "urls": {"Repository": "https://github.com/madebyjake/hashreport"},
    }
    config_mock.get_metadata.return_value = metadata
    return config_mock


@pytest.fixture
def sample_changelog():
    """Create a temporary changelog file for testing."""
    content = """# Changelog

## v1.0.0 (2023-05-15)
- Initial release
- Added core functionality

## v0.9.0 (2023-05-01)
- Beta release
- Fixed bugs
"""
    with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
        f.write(content)

    yield Path(f.name)
    Path(f.name).unlink()


def test_format_dependencies():
    """Test formatting of package dependencies."""
    deps = ["click", "rich", "tomli"]
    expected = "Requires:       python3-click\nRequires:       python3-rich\nRequires:       python3-tomli"  # noqa: E501
    assert format_dependencies(deps) == expected


def test_format_build_requires():
    """Test formatting of build requirements."""
    deps = ["wheel", "setuptools"]
    expected = "BuildRequires:  python3-wheel\nBuildRequires:  python3-setuptools"
    assert format_build_requires(deps).lower() == expected.lower()


def test_parse_changelog(sample_changelog):
    """Test parsing a changelog file."""
    entries = parse_changelog(sample_changelog)
    assert len(entries) == 2

    version1, date1, changes1 = entries[0]
    assert version1 == "1.0.0"
    assert date1 == "2023-05-15"
    assert "Initial release" in changes1
    assert "Added core functionality" in changes1

    version2, date2, changes2 = entries[1]
    assert version2 == "0.9.0"
    assert date2 == "2023-05-01"
    assert "Beta release" in changes2
    assert "Fixed bugs" in changes2


def test_parse_changelog_nonexistent_file():
    """Test parsing a nonexistent changelog file."""
    entries = parse_changelog(Path("nonexistent_file.md"))
    assert entries == []


def test_format_changelog_entries():
    """Test formatting changelog entries for RPM spec."""
    entries = [
        ("1.0.0", "2023-05-15", "Initial release\nAdded core functionality"),
        ("0.9.0", "2023-05-01", "Beta release\nFixed bugs"),
    ]

    packager = "Test User"
    version = "1.0.0"

    # Convert string date to expected RPM format
    date_obj = datetime.strptime("2023-05-15", "%Y-%m-%d")
    rpm_date = date_obj.strftime("%a %b %d %Y")

    expected = f"* {rpm_date} {packager} - 1.0.0-1\n- Initial release\n- Added core functionality"  # noqa: E501
    result = format_changelog_entries(entries, packager, version)
    assert result == expected


@patch("pathlib.Path.write_text")
@patch("tools.gen_spec.get_config")
def test_main(mock_get_config, mock_write_text, mock_config):
    """Test the main function that generates the spec file."""
    mock_get_config.return_value = mock_config

    with patch(
        "tools.gen_spec.parse_changelog",
        return_value=[("1.0.0", "2023-05-15", "Initial release")],
    ):
        from tools.gen_spec import main

        main()

        # Check that write_text was called
        mock_write_text.assert_called_once()

        # Verify spec content contains expected elements
        spec_content = mock_write_text.call_args[0][0]
        assert "Name:           hashreport" in spec_content
        assert "Version:        1.0.0" in spec_content
