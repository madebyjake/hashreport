"""CLI module for hashreport."""

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
from hashreport.utils.hasher import show_available_options
from hashreport.utils.scanner import get_report_filename, walk_directory_and_log
from hashreport.utils.viewer import ReportViewer
from hashreport.version import __version__

CONTEXT_SETTINGS = {"help_option_names": ["-h", "--help"], "max_content_width": 100}


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
        click.BadParameter: If size format is invalid
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
    """Handle errors for CLI commands."""
    click.echo(f"Error: {str(e)}", err=True)
    sys.exit(exit_code)


@click.group(context_settings=CONTEXT_SETTINGS)
@click.version_option(version=__version__, prog_name="hashreport")
def cli():
    """Generate hash reports for files in a directory."""
    pass


@cli.command()
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
    """
    Scan directory and generate hash report.

    DIRECTORY is the path to scan for files.
    """
    try:
        # Set default output path if none provided
        if not output:
            output = os.getcwd()

        # Handle email test mode
        if test_email:
            if not all([email, smtp_host]):
                raise click.BadParameter(
                    "Email and SMTP host are required for email testing"
                )
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
    except Exception as e:
        handle_error(e)


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
    """
    List files in the directory without generating hashes.

    DIRECTORY is the path to scan for files.
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
    except Exception as e:
        handle_error(e)


@cli.command()
@click.argument("report", type=click.Path(exists=True))
@click.option("-f", "--filter", "filter_text", help="Filter report entries")
def view(report: str, filter_text: Optional[str]) -> None:
    """View report contents with optional filtering."""
    try:
        viewer = ReportViewer()
        viewer.view_report(report, filter_text)
    except Exception as e:
        handle_error(e)


@cli.command()
@click.argument("report1", type=click.Path(exists=True))
@click.argument("report2", type=click.Path(exists=True))
@click.option(
    "-o", "--output", type=click.Path(), help="Output directory for comparison report"
)
def compare(report1: str, report2: str, output: Optional[str]) -> None:
    """Compare two reports and show differences."""
    try:
        viewer = ReportViewer()
        viewer.compare_reports(report1, report2, output)
    except Exception as e:
        handle_error(e)


cli.add_command(filelist)


@cli.command()
def algorithms():
    """Show available hash algorithms."""
    show_available_options()


@cli.group()
def config():
    """Manage configuration settings."""
    pass


@config.command()
def edit():
    """Edit configuration file in default editor."""
    try:
        settings_path = get_config().get_settings_path()
        if not settings_path.exists():
            # Create parent directories if they don't exist
            settings_path.parent.mkdir(parents=True, exist_ok=True)
            # Create empty config file
            settings_path.touch()
        click.edit(filename=str(settings_path))
    except Exception as e:
        handle_error(e)


@config.command()
def show():
    """Show current configuration settings."""
    try:
        console = Console()
        config_data = get_config().get_all_settings()
        console.print("\n[bold]Current Configuration[/bold]\n")
        print_section(config_data)
    except Exception as e:
        handle_error(e)


def print_section(data: Dict[str, Any], indent: int = 0) -> None:
    """Print configuration section with proper indentation."""
    try:
        for key, value in data.items():
            if isinstance(value, dict):
                console = Console()
                console.print(" " * indent + f"[bold]{key}[/bold]")
                print_section(value, indent + 2)
            else:
                console = Console()
                console.print(" " * indent + f"{key}: {value}")
    except Exception as e:
        raise Exception(f"Failed to print configuration: {e}")


# Add config commands to CLI
cli.add_command(config)

if __name__ == "__main__":
    cli()
