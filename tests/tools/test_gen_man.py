"""Test module for the gen_man tool."""

from unittest.mock import MagicMock, patch

import click
import pytest

from tools.gen_man import format_command, format_commands, format_global_options


@pytest.fixture
def mock_config():
    """Create a mock configuration object for testing."""
    config_mock = MagicMock()
    metadata = {
        "name": "hashreport",
        "version": "1.0.0",
        "description": "Generate detailed file hash reports",
        "authors": ["Test Author <test@example.com>"],
        "urls": {
            "Issues": "https://github.com/madebyjake/hashreport/issues",
            "Documentation": "https://github.com/madebyjake/hashreport",
        },
    }
    config_mock.get_metadata.return_value = metadata
    return config_mock


@pytest.fixture
def mock_cli_command():
    """Create a mock CLI command for testing."""

    @click.command("test")
    @click.option("--debug", is_flag=True, help="Enable debug mode")
    def test_command():
        """Test command help text."""
        pass

    return test_command


@pytest.fixture
def mock_cli_group():
    """Create a mock CLI group with commands for testing."""

    @click.group("testgroup")
    @click.option("--verbose", is_flag=True, help="Be verbose")
    def test_group():
        """Test group help text."""
        pass

    @test_group.command("subcommand")
    @click.argument("input_file")
    @click.option("--output", "-o", help="Output file")
    def subcommand(input_file, output):
        """Subcommand help text."""
        pass

    return test_group


@pytest.fixture
def mock_context(mock_cli_group):
    """Create a mock click context for testing."""
    return click.Context(mock_cli_group, info_name="hashreport")


def test_format_command_simple(mock_cli_command):
    """Test formatting a simple command for man page."""
    ctx = click.Context(mock_cli_command, info_name="hashreport")
    result = format_command(mock_cli_command, ctx)
    assert "\\fBtest\\fR" in result
    assert "Test command help text" in result
    assert "\\fB--debug\\fR" in result
    assert "Enable debug mode" in result


def test_format_command_group(mock_cli_group, mock_context):
    """Test formatting a command group for man page."""
    result = format_command(mock_cli_group, mock_context)

    # Check group formatting
    assert "\\fBtestgroup\\fR" in result
    assert "Test group help text" in result
    assert "\\fB--verbose\\fR" in result

    # Check subcommand formatting
    assert "\\fBtestgroup subcommand\\fR" in result
    assert "Subcommand help text" in result
    assert "\\fB--output\\fR" in result or "\\fB-o\\fR" in result


def test_format_commands(mock_context):
    """Test formatting all commands for man page."""

    @mock_context.command.command("simple")
    def simple():
        """Run a simple command."""
        pass

    result = format_commands(mock_context)

    assert "\\fBsimple\\fR" in result
    assert "Run a simple command" in result
    assert "\\fBsubcommand\\fR" in result
    assert "Subcommand help text" in result


def test_format_global_options(mock_context):
    """Test formatting global options for man page."""
    result = format_global_options(mock_context)

    assert "\\fB--verbose\\fR" in result
    assert "Be verbose" in result


@patch("pathlib.Path.write_text")
@patch("pathlib.Path.chmod")
@patch("pathlib.Path.mkdir")
@patch("tools.gen_man.get_config")
@patch("tools.gen_man.cli")
def test_generate_man_page(
    mock_cli, mock_get_config, mock_mkdir, mock_chmod, mock_write_text, mock_config
):
    """Test generating a man page from CLI commands and metadata."""
    mock_get_config.return_value = mock_config

    # Create a simple mock CLI structure
    @click.group()
    def mock_root_cli():
        """Root command description."""
        pass

    @mock_root_cli.command()
    def scan():
        """Scan command."""
        pass

    mock_cli.return_value = mock_root_cli

    from tools.gen_man import generate_man_page

    generate_man_page()

    # Verify directory was created
    mock_mkdir.assert_called_once()

    # Verify file was written
    mock_write_text.assert_called_once()
    man_content = mock_write_text.call_args[0][0]

    # Check basic man page content
    assert '.TH "HASHREPORT" "1"' in man_content
    assert "Test Author" in man_content

    # Verify permissions were set
    mock_chmod.assert_called_once()
