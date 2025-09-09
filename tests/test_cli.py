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
        assert "Internal Error" in result.output


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
    assert "Internal Error" in result.output


@patch("hashreport.cli.Console")
def test_config_show_error_handling(mock_console, tmp_path):
    """Test error handling in config show command."""
    mock_console.return_value.print.side_effect = Exception("Test error")
    runner = CliRunner()
    result = runner.invoke(cli, ["config", "show"])
    assert result.exit_code == 1
    assert "Internal Error" in result.output


def test_validate_size_invalid_formats():
    """Test validate_size with invalid formats."""
    from click import Context, Option

    from hashreport.cli import validate_size

    ctx = Context(click.Command("test"))
    param = Option(["--test"], "test")

    invalid_sizes = [
        "abc",  # No number
        "123",  # No unit
        "123XYZ",  # Invalid unit
        "abcKB",  # No number
        "1.2.3KB",  # Invalid number
        "0KB",  # Zero size
        "-1KB",  # Negative size
    ]

    for size_str in invalid_sizes:
        with pytest.raises(click.BadParameter, match="Invalid size format"):
            validate_size(ctx, param, size_str)


def test_validate_size_valid_formats():
    """Test validate_size with valid formats."""
    from click import Context, Option

    from hashreport.cli import validate_size

    ctx = Context(click.Command("test"))
    param = Option(["--test"], "test")

    valid_sizes = [
        "1B",
        "1KB",
        "1MB",
        "1GB",
        "1.5KB",
        "2.5MB",
    ]

    for size_str in valid_sizes:
        result = validate_size(ctx, param, size_str)
        assert result == size_str


def test_validate_size_none():
    """Test validate_size with None value."""
    from click import Context, Option

    from hashreport.cli import validate_size

    ctx = Context(click.Command("test"))
    param = Option(["--test"], "test")

    result = validate_size(ctx, param, None)
    assert result is None


def test_handle_error_hashreport_error(caplog):
    """Test handle_error with HashReportError."""
    from hashreport.cli import handle_error
    from hashreport.utils.exceptions import HashReportError

    error = HashReportError("Test error")

    with pytest.raises(SystemExit) as exc_info:
        handle_error(error)

    assert exc_info.value.code == 1
    assert "Test error" in caplog.text


def test_handle_error_click_bad_parameter(caplog):
    """Test handle_error with click.BadParameter."""
    from hashreport.cli import handle_error

    error = click.BadParameter("Invalid parameter")

    with pytest.raises(SystemExit) as exc_info:
        handle_error(error)

    assert exc_info.value.code == 1
    assert "Invalid parameter" in caplog.text


def test_handle_error_generic_exception(caplog):
    """Test handle_error with generic exception."""
    from hashreport.cli import handle_error

    error = ValueError("Generic error")

    with pytest.raises(SystemExit) as exc_info:
        handle_error(error)

    assert exc_info.value.code == 1
    assert "Internal error" in caplog.text


def test_validate_email_options_missing_email():
    """Test validate_email_options with missing email."""
    from hashreport.cli import validate_email_options

    with pytest.raises(click.BadParameter, match="Email and SMTP host are required"):
        validate_email_options(None, "smtp.example.com")


def test_validate_email_options_missing_smtp_host():
    """Test validate_email_options with missing SMTP host."""
    from hashreport.cli import validate_email_options

    with pytest.raises(click.BadParameter, match="Email and SMTP host are required"):
        validate_email_options("test@example.com", None)


def test_validate_email_options_valid():
    """Test validate_email_options with valid parameters."""
    from hashreport.cli import validate_email_options

    # Should not raise any exception
    validate_email_options("test@example.com", "smtp.example.com")


def test_scan_command_with_default_output(tmp_path):
    """Test scan command with default output directory."""
    runner = CliRunner()
    input_dir = tmp_path / "input"
    input_dir.mkdir()

    with patch("hashreport.cli.walk_directory_and_log") as mock_walk:
        with patch("hashreport.cli.os.getcwd", return_value=str(tmp_path)):
            result = runner.invoke(cli, ["scan", str(input_dir)])
            assert result.exit_code == 0
            mock_walk.assert_called_once()


def test_scan_command_test_email_mode(tmp_path):
    """Test scan command in test email mode."""
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
        mock_walk.assert_not_called()  # Should not process files in test mode


def test_scan_command_test_email_missing_params(tmp_path):
    """Test scan command test email mode with missing parameters."""
    runner = CliRunner()
    input_dir = tmp_path / "input"
    input_dir.mkdir()

    command = [
        "scan",
        str(input_dir),
        "--test-email",
        "--email",
        "test@example.com",
        # Missing --smtp-host
    ]

    result = runner.invoke(cli, command)
    assert result.exit_code == 2  # Click error code
    assert "Email and SMTP host are required" in result.output


def test_filelist_command_with_default_output(tmp_path):
    """Test filelist command with default output directory."""
    runner = CliRunner()
    input_dir = tmp_path / "input"
    input_dir.mkdir()

    with patch("hashreport.cli.list_files_in_directory") as mock_list:
        with patch("hashreport.cli.os.getcwd", return_value=str(tmp_path)):
            result = runner.invoke(cli, ["filelist", str(input_dir)])
            assert result.exit_code == 0
            mock_list.assert_called_once()


def test_filelist_command_error_handling(tmp_path):
    """Test filelist command error handling."""
    runner = CliRunner()
    input_dir = tmp_path / "input"
    input_dir.mkdir()

    with patch("hashreport.cli.list_files_in_directory") as mock_list:
        mock_list.side_effect = Exception("Test error")
        result = runner.invoke(cli, ["filelist", str(input_dir)])
        assert result.exit_code == 1
        assert "Internal Error" in result.output


def test_view_command_error_handling(tmp_path):
    """Test view command error handling."""
    runner = CliRunner()
    report_file = tmp_path / "report.json"
    report_file.touch()

    with patch("hashreport.cli.ReportViewer") as mock_viewer:
        mock_viewer.return_value.view_report.side_effect = Exception("Test error")
        result = runner.invoke(cli, ["view", str(report_file)])
        assert result.exit_code == 1
        assert "Internal Error" in result.output


def test_compare_command_error_handling(tmp_path):
    """Test compare command error handling."""
    runner = CliRunner()
    report1 = tmp_path / "report1.json"
    report2 = tmp_path / "report2.json"
    report1.touch()
    report2.touch()

    with patch("hashreport.cli.ReportViewer") as mock_viewer:
        mock_viewer.return_value.compare_reports.side_effect = Exception("Test error")
        result = runner.invoke(cli, ["compare", str(report1), str(report2)])
        assert result.exit_code == 1
        assert "Internal Error" in result.output


def test_scan_command_hashreport_error(tmp_path):
    """Test scan command with HashReportError."""
    runner = CliRunner()
    input_dir = tmp_path / "input"
    input_dir.mkdir()

    with patch("hashreport.cli.walk_directory_and_log") as mock_walk:
        from hashreport.utils.exceptions import HashReportError

        mock_walk.side_effect = HashReportError("Test error")
        result = runner.invoke(cli, ["scan", str(input_dir)])
        assert result.exit_code == 2
        assert "Test error" in result.output


def test_scan_command_click_bad_parameter(tmp_path):
    """Test scan command with click.BadParameter."""
    runner = CliRunner()
    input_dir = tmp_path / "input"
    input_dir.mkdir()

    with patch("hashreport.cli.walk_directory_and_log") as mock_walk:
        mock_walk.side_effect = click.BadParameter("Invalid parameter")
        result = runner.invoke(cli, ["scan", str(input_dir)])
        assert result.exit_code == 2
        assert "Invalid parameter" in result.output


def test_validate_size_edge_cases():
    """Test validate_size with edge cases."""
    from click import Context, Option

    from hashreport.cli import validate_size

    ctx = Context(click.Command("test"))
    param = Option(["--test"], "test")

    # Test empty string (should return None)
    result = validate_size(ctx, param, "")
    assert result is None

    # Test whitespace only
    with pytest.raises(click.BadParameter, match="Size must include unit"):
        validate_size(ctx, param, "   ")

    # Test very large number
    result = validate_size(ctx, param, "999999999GB")
    assert result == "999999999GB"

    # Test decimal with zero
    result = validate_size(ctx, param, "0.5MB")
    assert result == "0.5MB"

    # Test zero size (should fail)
    with pytest.raises(click.BadParameter, match="Size must be greater than 0"):
        validate_size(ctx, param, "0MB")


def test_handle_error_with_exit_code():
    """Test handle_error with custom exit code."""
    from hashreport.cli import handle_error
    from hashreport.utils.exceptions import HashReportError

    error = HashReportError("Test error")

    with pytest.raises(SystemExit) as exc_info:
        handle_error(error, exit_code=3)

    assert exc_info.value.code == 3


def test_print_section_recursive():
    """Test print_section with nested data."""
    from rich.console import Console

    from hashreport.cli import print_section

    console = Console()
    data = {"level1": {"level2": {"level3": "value"}}, "simple": "value"}

    # Should not raise any exception
    print_section(console, data)


def test_print_section_error_handling():
    """Test print_section error handling."""
    from rich.console import Console

    from hashreport.cli import print_section

    console = Console()
    data = {"key": "value"}

    # Mock console.print to raise an exception
    with patch.object(console, "print", side_effect=Exception("Print error")):
        with pytest.raises(Exception, match="Failed to print configuration"):
            print_section(console, data)
