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
from hashreport.utils.exceptions import ConfigError
from hashreport.utils.hasher import show_available_options
from hashreport.utils.scanner import get_report_filename, walk_directory_and_log
from hashreport.utils.viewer import ReportViewer

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
@click.version_option(
    version=get_config().version,
    prog_name=get_config().name,
    message="%(prog)s version %(version)s\n"
    f"Author: {', '.join(get_config().authors)}\n"
    f"License: {get_config().project_license}",
)
def cli():
    r"""
    Generate hash reports for files in a directory.

    {name} {version} - {description}

    {license} License

    {docs}
    """.format(
        name=get_config().name.title(),
        version=get_config().version,
        description=get_config().description,
        license=get_config().project_license,
        docs=get_config().urls.get("documentation", ""),
    )


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
    viewer = ReportViewer()
    try:
        viewer.display_report(report, filter_text)
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
    viewer = ReportViewer()
    try:
        changes = viewer.compare_reports(report1, report2)
        viewer.display_comparison(changes)
        if output:
            viewer.save_comparison(changes, output, report1, report2)
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
@click.argument("output_path", type=click.Path(), required=False)
def init(output_path: Optional[str]):
    """Generate a default settings file."""
    return _create_default_settings(output_path)


def _create_default_settings(output_path: Optional[str] = None) -> Optional[Path]:
    """Create a default settings file.

    Args:
        output_path: Optional custom path for settings file

    Returns:
        Path to created settings file or None if creation failed
    """
    try:
        default_config = Path(__file__).parent / "default_config.toml"
        target_path = Path(
            output_path if output_path else get_config().get_settings_path()
        )

        # Create parent directories if they don't exist
        target_path.parent.mkdir(parents=True, exist_ok=True)

        with default_config.open("r") as src, target_path.open("w") as dst:
            dst.write(src.read())

        click.echo(f"Created default settings at {target_path}")
        return target_path
    except Exception as e:
        handle_error(e)


@config.command()
def edit():
    """Edit user settings using system default editor."""
    try:
        config_path = get_config().get_settings_path()

        if not config_path.exists():
            if click.confirm("Settings file not found. Create one?"):
                config_path = _create_default_settings()
            else:
                return

        if not config_path or not config_path.exists():
            click.echo("No settings file available to edit.", err=True)
            return

        click.edit(filename=str(config_path))

        # Reload config to verify changes
        try:
            get_config()
            click.echo("Settings updated successfully.")
        except ConfigError as e:
            click.echo(f"Warning: The edited settings may have errors: {e}", err=True)

    except Exception as e:
        handle_error(e)


@config.command()
def show():
    """Show all active configuration settings."""
    try:
        cfg = get_config()
        settings_path = cfg.get_settings_path()
        console = Console()

        console.print("\n[bold blue]Current Configuration:[/bold blue]")
        console.print(f"[dim]Settings file: {settings_path}[/dim]\n")

        def print_section(data: Dict[str, Any], indent: int = 0) -> None:
            for key, value in sorted(data.items()):
                prefix = "  " * indent
                if isinstance(value, dict):
                    console.print(f"{prefix}[yellow]{key}:[/yellow]")
                    print_section(value, indent + 1)
                else:
                    console.print(f"{prefix}{key} = {value}")

        print_section(cfg.get_all_settings())

    except Exception as e:
        handle_error(e)


# Add config commands to CLI
cli.add_command(config)

if __name__ == "__main__":
    cli()
