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


@patch("hashreport.cli.click.edit")
def test_config_edit(mock_edit, tmp_path):
    """Test config edit command."""
    config_path = tmp_path / "settings.toml"
    config_path.parent.mkdir(parents=True, exist_ok=True)

    with patch("hashreport.config.HashReportConfig.get_settings_path") as mock_path:
        mock_path.return_value = config_path
        runner = CliRunner()
        result = runner.invoke(cli, ["config", "edit"])

        assert result.exit_code == 0
        assert config_path.exists()  # Verify file was created
        mock_edit.assert_called_once_with(filename=str(config_path))


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


def test_scan_error_handling(tmp_path):
    """Test error handling in scan command."""
    runner = CliRunner()
    input_dir = tmp_path / "input"
    input_dir.mkdir()

    with patch("hashreport.cli.walk_directory_and_log") as mock_walk:
        mock_walk.side_effect = Exception("Test error")
        result = runner.invoke(cli, ["scan", str(input_dir)])
        assert result.exit_code == 1
        assert "Error: Test error" in result.output


def test_scan_email_configuration(tmp_path):
    """Test email configuration in scan command."""
    runner = CliRunner()
    input_dir = tmp_path / "input"
    input_dir.mkdir()

    # Test with email options
    command = [
        "scan",
        str(input_dir),
        "--email",
        "test@example.com",
        "--smtp-host",
        "smtp.example.com",
        "--smtp-port",
        "587",
        "--smtp-user",
        "user",
        "--smtp-password",
        "pass",
    ]

    with patch("hashreport.cli.walk_directory_and_log") as mock_walk:
        result = runner.invoke(cli, command)
        assert result.exit_code == 0
        mock_walk.assert_called_once()


def test_scan_test_email(tmp_path):
    """Test email configuration testing."""
    runner = CliRunner()
    input_dir = tmp_path / "input"
    input_dir.mkdir()

    command = [
        "scan",
        str(input_dir),
        "--test-email",
        "--email",
        "test@example.com",
        "--smtp-host",
        "smtp.example.com",
    ]

    with patch("hashreport.cli.walk_directory_and_log") as mock_walk:
        result = runner.invoke(cli, command)
        assert result.exit_code == 0
        mock_walk.assert_not_called()


@patch("hashreport.cli.list_files_in_directory")
def test_filelist_command(mock_list, tmp_path):
    """Test filelist command."""
    runner = CliRunner()
    input_dir = tmp_path / "input"
    output_dir = tmp_path / "output"
    input_dir.mkdir()

    result = runner.invoke(cli, ["filelist", str(input_dir), "-o", str(output_dir)])
    assert result.exit_code == 0
    mock_list.assert_called_once_with(str(input_dir), str(output_dir), recursive=True)


@patch("hashreport.cli.ReportViewer")
def test_view_command(mock_viewer, tmp_path):
    """Test view command."""
    runner = CliRunner()
    report_file = tmp_path / "report.json"
    report_file.touch()

    # Test without filter
    result = runner.invoke(cli, ["view", str(report_file)])
    assert result.exit_code == 0
    mock_viewer.return_value.view_report.assert_called_once_with(str(report_file), None)

    # Test with filter
    result = runner.invoke(cli, ["view", str(report_file), "--filter", "test"])
    assert result.exit_code == 0
    mock_viewer.return_value.view_report.assert_called_with(str(report_file), "test")


@patch("hashreport.cli.ReportViewer")
def test_compare_command(mock_viewer, tmp_path):
    """Test compare command."""
    runner = CliRunner()
    report1 = tmp_path / "report1.json"
    report2 = tmp_path / "report2.json"
    output_dir = tmp_path / "output"
    report1.touch()
    report2.touch()
    output_dir.mkdir()

    # Test without output directory
    result = runner.invoke(cli, ["compare", str(report1), str(report2)])
    assert result.exit_code == 0
    mock_viewer.return_value.compare_reports.assert_called_once_with(
        str(report1), str(report2), None
    )

    # Test with output directory
    result = runner.invoke(
        cli, ["compare", str(report1), str(report2), "-o", str(output_dir)]
    )
    assert result.exit_code == 0
    mock_viewer.return_value.compare_reports.assert_called_with(
        str(report1), str(report2), str(output_dir)
    )


@patch("hashreport.cli.click.edit")
def test_config_edit_error_handling(mock_edit, tmp_path):
    """Test error handling in config edit command."""
    mock_edit.side_effect = Exception("Test error")
    runner = CliRunner()
    result = runner.invoke(cli, ["config", "edit"])
    assert result.exit_code == 1
    assert "Error: Test error" in result.output


@patch("hashreport.cli.Console")
def test_config_show_error_handling(mock_console, tmp_path):
    """Test error handling in config show command."""
    mock_console.return_value.print.side_effect = Exception("Test error")
    runner = CliRunner()
    result = runner.invoke(cli, ["config", "show"])
    assert result.exit_code == 1
    assert "Error: Test error" in result.output
