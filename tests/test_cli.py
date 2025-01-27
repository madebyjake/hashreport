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
