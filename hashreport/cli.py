"""CLI module for hashreport.

This module provides the command-line interface for the hashreport tool.
It includes commands for scanning directories, generating reports, and managing configuration.

Example:
    $ hashreport scan /path/to/dir -o output.json
    $ hashreport view report.json --filter "*.txt"
    $ hashreport config show
"""  # noqa: E501

import logging
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

import click
from rich.console import Console

from hashreport.config import get_config
from hashreport.reports.filelist_handler import (
    get_filelist_filename,
    list_files_in_directory,
)
from hashreport.utils.exceptions import HashReportError
from hashreport.utils.hasher import show_available_options
from hashreport.utils.scanner import get_report_filename, walk_directory_and_log
from hashreport.utils.viewer import ReportViewer
from hashreport.version import __version__

CONTEXT_SETTINGS = {"help_option_names": ["-h", "--help"], "max_content_width": 100}

logger = logging.getLogger("hashreport.cli")


def validate_size(
    ctx: click.Context, param: click.Parameter, value: Optional[str]
) -> Optional[str]:
    """Validate and convert size parameter format.

    Args:
        ctx: Click context
        param: Click parameter
        value: Size string with unit (e.g., "1MB", "500KB")

    Returns:
        Valid size string or None if no value provided

    Raises:
        click.BadParameter: If size format is invalid or size is not positive

    Example:
        >>> validate_size(None, None, "1MB")
        '1MB'
        >>> validate_size(None, None, "invalid")
        Traceback (most recent call last):
            ...
            click.BadParameter: Invalid size format: Size must include unit...
    """
    if not value:
        return None

    units = {
        "B": 1,
        "KB": 1024,
        "MB": 1024 * 1024,
        "GB": 1024 * 1024 * 1024,
    }

    try:
        size = value.strip().upper()
        # Sort units by length (longest first) to avoid partial matches
        sorted_units = sorted(units.keys(), key=len, reverse=True)

        # Find matching unit
        matched_unit = None
        for unit in sorted_units:
            if size.endswith(unit):
                matched_unit = unit
                break

        if not matched_unit:
            raise ValueError(
                f"Size must include unit. Valid units are: {', '.join(sorted_units)}"
            )

        # Extract numeric part by removing the unit
        number_str = size[: -len(matched_unit)]
        if not number_str:
            raise ValueError("No numeric value provided")

        # Validate number can be converted
        number = float(number_str)
        if number <= 0:
            raise ValueError("Size must be greater than 0")

        return value

    except (ValueError, AttributeError) as e:
        raise click.BadParameter(f"Invalid size format: {e}")


def handle_error(e: Exception, exit_code: int = 1) -> None:
    """Handle errors for CLI commands with user-friendly output and logging.

    Args:
        e: The exception that occurred
        exit_code: The exit code to use (default: 1)
    """
    import traceback

    if isinstance(e, (HashReportError, click.BadParameter)):
        click.echo(f"[Error] {e}", err=True)
        logger.warning(f"User error: {e}")
    else:
        click.echo(
            "[Internal Error] An unexpected error occurred. "
            "Please report this issue if it persists.",
            err=True,
        )
        logger.error(f"Internal error: {e}")
        logger.error(traceback.format_exc())
    sys.exit(exit_code)


@click.group(context_settings=CONTEXT_SETTINGS)
@click.version_option(version=__version__, prog_name="hashreport")
def cli():
    """Generate hash reports for files in a directory.

    This tool helps you generate and manage hash reports for files in a directory.
    It supports multiple hash algorithms, output formats, and filtering options.

    Example:
        $ hashreport scan /path/to/dir -o output.json
        $ hashreport view report.json --filter "*.txt"
        $ hashreport config show
    """
    pass


def validate_email_options(email, smtp_host):
    """Validate email-related CLI options."""
    if not all([email, smtp_host]):
        raise click.BadParameter("Email and SMTP host are required for email testing")


@cli.command(name="scan")
@click.argument("directory", type=click.Path(exists=True, file_okay=False))
@click.option("-o", "--output", type=click.Path(), help="Output directory path")
@click.option(
    "-a",
    "--algorithm",
    default=get_config().default_algorithm,
    help="Hash algorithm to use",
)
@click.option(
    "-f",
    "--format",
    "output_formats",
    multiple=True,
    type=click.Choice(get_config().supported_formats),
    default=[get_config().default_format],
    help="Output formats (csv, json)",
)
@click.option(
    "--min-size",
    "min_size",
    callback=validate_size,
    help="Minimum file size (e.g., 1MB)",
)
@click.option(
    "--max-size",
    "max_size",
    callback=validate_size,
    help="Maximum file size (e.g., 1GB)",
)
@click.option(
    "--include",
    multiple=True,
    help="Include files matching pattern (can be used multiple times)",
)
@click.option(
    "--exclude",
    multiple=True,
    help="Exclude files matching pattern (can be used multiple times)",
)
@click.option(
    "--regex", is_flag=True, help="Use regex for pattern matching instead of glob"
)
@click.option("--limit", type=int, help="Limit the number of files to process")
@click.option("--email", help="Email address to send report to")
@click.option("--smtp-host", help="SMTP server host")
@click.option("--smtp-port", type=int, default=587, help="SMTP server port")
@click.option("--smtp-user", help="SMTP username")
@click.option("--smtp-password", help="SMTP password")
@click.option(
    "--test-email",
    is_flag=True,
    help="Test email configuration without processing files",
)
@click.option(
    "--recursive/--no-recursive",
    default=True,
    help="Recursively process subdirectories (recursive by default)",
)
def scan(
    directory: str,
    output: str,
    algorithm: str,
    output_formats: List[str],
    min_size: str,
    max_size: str,
    include: tuple,
    exclude: tuple,
    regex: bool,
    limit: int,
    email: str,
    smtp_host: str,
    smtp_port: int,
    smtp_user: str,
    smtp_password: str,
    test_email: bool,
    recursive: bool,
):
    """Scan directory and generate hash report.

    This command scans the specified directory and generates a hash report for all files.
    The report can be output in multiple formats and can be filtered by various criteria.

    Args:
        directory: Path to scan for files
        output: Output directory path (default: current directory)
        algorithm: Hash algorithm to use
        output_formats: List of output formats to generate
        min_size: Minimum file size to include
        max_size: Maximum file size to include
        include: List of patterns to include
        exclude: List of patterns to exclude
        regex: Whether to use regex for pattern matching
        limit: Maximum number of files to process
        email: Email address to send report to
        smtp_host: SMTP server host
        smtp_port: SMTP server port
        smtp_user: SMTP username
        smtp_password: SMTP password
        test_email: Whether to test email configuration only
        recursive: Whether to process subdirectories

    Example:
        $ hashreport scan /path/to/dir -o output.json -a sha256 -f json
        $ hashreport scan /path/to/dir --min-size 1MB --max-size 1GB --include "*.txt"
    """  # noqa: E501
    try:
        # Set default output path if none provided
        if not output:
            output = os.getcwd()

        # Handle email test mode
        if test_email:
            validate_email_options(email, smtp_host)
            # Test email configuration without processing files
            return

        # Create output files with explicit formats
        output_files = [
            (
                get_report_filename(output, output_format=fmt)
                if not output.endswith(f".{fmt}")
                else output
            )
            for fmt in output_formats
        ]

        walk_directory_and_log(
            directory,
            output_files,
            algorithm=algorithm,
            min_size=min_size,
            max_size=max_size,
            include=include,
            exclude=exclude,
            regex=regex,
            limit=limit,
            recursive=recursive,
        )
    except (HashReportError, click.BadParameter) as e:
        handle_error(e, exit_code=2)
    except Exception as e:
        handle_error(e, exit_code=1)


@cli.command()
@click.argument("directory", type=click.Path(exists=True, file_okay=False))
@click.option("-o", "--output", type=click.Path(), help="Output file path")
@click.option(
    "--recursive/--no-recursive",
    default=True,
    help="Recursively process subdirectories (recursive by default)",
)
def filelist(
    directory: str,
    output: str,
    recursive: bool,
):
    """List files in the directory without generating hashes.

    This command generates a list of files in the specified directory without
    calculating their hashes. This is useful for quick directory analysis or
    when you only need a file listing.

    Args:
        directory: Path to scan for files
        output: Output file path (default: current directory)
        recursive: Whether to process subdirectories

    Example:
        $ hashreport filelist /path/to/dir -o files.txt
        $ hashreport filelist /path/to/dir --no-recursive
    """
    try:
        # Set default output path if none provided
        if not output:
            output = os.getcwd()

        output_file = get_filelist_filename(output)
        output_dir = Path(output_file).parent
        output_dir.mkdir(parents=True, exist_ok=True)

        list_files_in_directory(
            directory,
            output_file,
            recursive=recursive,
        )
    except (HashReportError, click.BadParameter) as e:
        handle_error(e, exit_code=2)
    except Exception as e:
        handle_error(e, exit_code=1)


@cli.command()
@click.argument("report", type=click.Path(exists=True))
@click.option("-f", "--filter", "filter_text", help="Filter report entries")
def view(report: str, filter_text: Optional[str]) -> None:
    """View report contents with optional filtering.

    This command displays the contents of a hash report with optional filtering.
    The report can be filtered using glob patterns or regular expressions.

    Args:
        report: Path to the report file
        filter_text: Optional filter pattern to apply

    Example:
        $ hashreport view report.json
        $ hashreport view report.json --filter "*.txt"
    """
    try:
        viewer = ReportViewer()
        viewer.view_report(report, filter_text)
    except (HashReportError, click.BadParameter) as e:
        handle_error(e, exit_code=2)
    except Exception as e:
        handle_error(e, exit_code=1)


@cli.command()
@click.argument("report1", type=click.Path(exists=True))
@click.argument("report2", type=click.Path(exists=True))
@click.option(
    "-o", "--output", type=click.Path(), help="Output directory for comparison report"
)
def compare(report1: str, report2: str, output: Optional[str]) -> None:
    """Compare two reports and show differences.

    This command compares two hash reports and shows the differences between them.
    It can be useful for detecting changes in file hashes over time.

    Args:
        report1: Path to the first report file
        report2: Path to the second report file
        output: Optional output directory for the comparison report

    Example:
        $ hashreport compare report1.json report2.json
        $ hashreport compare report1.json report2.json -o diff/
    """
    try:
        viewer = ReportViewer()
        viewer.compare_reports(report1, report2, output)
    except (HashReportError, click.BadParameter) as e:
        handle_error(e, exit_code=2)
    except Exception as e:
        handle_error(e, exit_code=1)


@cli.command()
def algorithms():
    """Show available hash algorithms.

    This command displays a list of all available hash algorithms that can be used
    for generating reports.

    Example:
        $ hashreport algorithms
    """
    show_available_options()


@cli.group()
def config():
    """Manage configuration settings.

    This command group provides tools for managing the hashreport configuration.
    You can view, edit, and customize various settings.

    Example:
        $ hashreport config show
        $ hashreport config edit
    """
    pass


@config.command()
def edit():
    """Edit configuration file in default editor.

    This command opens the configuration file in your default text editor.
    If the file doesn't exist, it will be created with default settings.

    Example:
        $ hashreport config edit
    """
    try:
        settings_path = get_config().get_settings_path()
        if not settings_path.exists():
            settings_path.parent.mkdir(parents=True, exist_ok=True)
            settings_path.touch()
        click.edit(filename=str(settings_path))
    except (HashReportError, click.BadParameter) as e:
        handle_error(e, exit_code=2)
    except Exception as e:
        handle_error(e, exit_code=1)


@config.command()
def show():
    """Show current configuration settings.

    This command displays all current configuration settings in a formatted way.
    It shows both default and custom settings.

    Example:
        $ hashreport config show
    """
    try:
        console = Console()
        config = get_config()
        config_data = config.to_dict()
        console.print("\n[bold]Current Configuration[/bold]\n")
        print_section(console, config_data)
    except (HashReportError, click.BadParameter) as e:
        handle_error(e, exit_code=2)
    except Exception as e:
        handle_error(e, exit_code=1)


def print_section(console: Console, data: Dict[str, Any], indent: int = 0) -> None:
    """Print configuration section with proper indentation.

    This function recursively prints configuration data with proper formatting
    and indentation using the Rich console.

    Args:
        console: Rich console instance for output
        data: Configuration data to print
        indent: Current indentation level

    Raises:
        Exception: If there's an error printing the configuration
    """
    try:
        for key, value in data.items():
            if isinstance(value, dict):
                console.print(" " * indent + f"[bold]{key}[/bold]")
                print_section(console, value, indent + 2)
            else:
                console.print(" " * indent + f"{key}: {value}")
    except Exception as e:
        raise Exception(f"Failed to print configuration: {e}")


# Add config commands to CLI
cli.add_command(config)

if __name__ == "__main__":
    cli()
