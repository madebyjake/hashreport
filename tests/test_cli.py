"""Tests for the CLI module."""

from unittest.mock import patch

import click
import pytest
from click.testing import CliRunner

from hashreport.cli import cli, validate_size


def test_validate_size():
    """Test size parameter validation."""
    ctx = None
    param = None
    if validate_size(ctx, param, "1MB") != "1MB":
        pytest.fail("Expected valid size '1MB' to pass validation")
    if validate_size(ctx, param, None) is not None:
        pytest.fail("Expected None to pass validation")

    with pytest.raises(click.BadParameter, match="Size must include unit"):
        validate_size(ctx, param, "1")  # Missing unit

    with pytest.raises(click.BadParameter, match="Size must include unit"):
        validate_size(ctx, param, "invalid")  # Invalid format


def test_cli_version():
    """Test version command."""
    runner = CliRunner()
    result = runner.invoke(cli, ["--version"])
    if result.exit_code != 0:
        pytest.fail("Version command failed")


@patch("hashreport.cli.walk_directory_and_log")
def test_scan_command(mock_walk, tmp_path):
    """Test scan command with basic options."""
    runner = CliRunner()
    input_dir = tmp_path / "input"
    output_dir = tmp_path / "output"
    input_dir.mkdir()

    result = runner.invoke(
        cli, ["scan", str(input_dir), "-o", str(output_dir), "-f", "csv", "-f", "json"]
    )
    assert result.exit_code == 0

    # Get the actual calls to the mock
    mock_calls = mock_walk.call_args_list
    assert len(mock_calls) == 1

    args, kwargs = mock_calls[0]
    assert args[0] == str(input_dir)
    assert len(args[1]) == 2  # Two output files
    assert any(f.endswith(".csv") for f in args[1])
    assert any(f.endswith(".json") for f in args[1])


@patch("hashreport.cli.walk_directory_and_log")
def test_multiple_formats(mock_walk, tmp_path):
    """Test scan command with multiple output formats."""
    runner = CliRunner()
    input_dir = tmp_path / "input"
    output_dir = tmp_path / "output"
    input_dir.mkdir()

    result = runner.invoke(
        cli, ["scan", str(input_dir), "-o", str(output_dir), "-f", "json", "-f", "csv"]
    )

    assert result.exit_code == 0

    # Verify walk_directory_and_log was called with correct arguments
    args, _ = mock_walk.call_args
    assert len(args[1]) == 2  # Two output files
    assert any(".json" in f for f in args[1])
    assert any(".csv" in f for f in args[1])


@patch("hashreport.cli.walk_directory_and_log")
def test_scan_format_handling(mock_walk, tmp_path):
    """Test scan command respects format option."""
    runner = CliRunner()
    input_dir = tmp_path / "input"
    output_dir = tmp_path / "output"
    input_dir.mkdir()
    output_dir.mkdir()

    # Test with single format
    result = runner.invoke(
        cli, ["scan", str(input_dir), "-o", str(output_dir), "--format", "json"]
    )
    assert result.exit_code == 0
    args, _ = mock_walk.call_args
    assert len(args[1]) == 1  # One output file
    assert args[1][0].endswith(".json")  # Should have json extension

    # Test explicit output path with extension
    result = runner.invoke(
        cli,
        [
            "scan",
            str(input_dir),
            "-o",
            str(output_dir / "report.csv"),
            "--format",
            "json",
        ],
    )
    assert result.exit_code == 0
    args, _ = mock_walk.call_args
    assert args[1][0].endswith(".json")  # Format should override existing extension


@patch("hashreport.cli.show_available_options")
def test_algorithms_command(mock_show):
    """Test algorithms command."""
    runner = CliRunner()
    result = runner.invoke(cli, ["algorithms"])
    if result.exit_code != 0:
        pytest.fail("Algorithms command failed")
    mock_show.assert_called_once()


def test_invalid_directory():
    """Test scan with nonexistent directory."""
    runner = CliRunner()
    result = runner.invoke(cli, ["scan", "/nonexistent/path"])
    if result.exit_code == 0:
        pytest.fail("Expected error for nonexistent directory")


def test_scan_with_options(tmp_path):
    """Test scan command with various options."""
    runner = CliRunner()
    input_dir = tmp_path / "input"
    output_file = tmp_path / "report.json"
    input_dir.mkdir()

    command = [
        "scan",
        str(input_dir),
        "-o",
        str(output_file),
        "-a",
        "sha256",
        "-f",
        "json",
        "--min-size",
        "1MB",
        "--max-size",
        "1GB",
        "--include",
        "*.txt",
        "--exclude",
        "*.tmp",
        "--limit",
        "10",
    ]

    with patch("hashreport.cli.walk_directory_and_log") as mock_walk:
        result = runner.invoke(cli, command)
        assert result.exit_code == 0, f"Command failed: {result.output}"

        mock_walk.assert_called_once()
        args, kwargs = mock_walk.call_args

        assert args[0] == str(input_dir)  # Input directory
        assert len(args[1]) == 1  # One output file
        assert args[1][0].endswith(".json")  # JSON extension
        assert kwargs.get("algorithm") == "sha256"


@patch("hashreport.cli._create_default_settings")
def test_config_init(mock_create, tmp_path):
    """Test config init command."""
    runner = CliRunner()
    result = runner.invoke(cli, ["config", "init"])
    assert result.exit_code == 0
    mock_create.assert_called_once_with(None)

    # Test with custom path
    custom_path = tmp_path / "config.toml"
    result = runner.invoke(cli, ["config", "init", str(custom_path)])
    assert result.exit_code == 0
    mock_create.assert_called_with(str(custom_path))


@patch("hashreport.cli.click.edit")
@patch("hashreport.cli._create_default_settings")
def test_config_edit(mock_create, mock_edit, tmp_path):
    """Test config edit command."""
    config_path = tmp_path / "settings.toml"
    config_path.touch()

    with patch("hashreport.config.HashReportConfig.get_settings_path") as mock_path:
        mock_path.return_value = config_path
        runner = CliRunner()
        result = runner.invoke(cli, ["config", "edit"])

        assert result.exit_code == 0
        mock_edit.assert_called_once_with(filename=str(config_path))
        mock_create.assert_not_called()


@patch("hashreport.cli.Console")
def test_config_show(mock_console, tmp_path):
    """Test config show command."""
    runner = CliRunner()
    result = runner.invoke(cli, ["config", "show"])
    assert result.exit_code == 0

    console = mock_console.return_value
    assert console.print.called
    # Verify section headers were printed
    calls = console.print.call_args_list
    assert any("Current Configuration" in str(c) for c in calls)
