"""CLI module for hashreport."""

import os
from typing import List, Optional

import click
from rich.console import Console

from hashreport.const import global_const
from hashreport.utils.hasher import show_available_options
from hashreport.utils.scanner import walk_directory_and_log

console = Console()

CONTEXT_SETTINGS = {"help_option_names": ["-h", "--help"], "max_content_width": 100}


def validate_size(ctx, param, value):
    """Validate size parameter format."""
    if not value:
        return None
    try:
        if not any(unit in value.upper() for unit in ["B", "KB", "MB", "GB"]):
            raise click.BadParameter("Size must include unit (B, KB, MB, GB)")
        return value
    except ValueError:
        raise click.BadParameter("Invalid size format")


@click.group(context_settings=CONTEXT_SETTINGS)
@click.version_option(version=global_const.VERSION)
def cli():
    r"""
    Generate hash reports for files in a directory.

    hashreport is a command-line tool that generates comprehensive hash reports
    for files within a directory. The reports include file details such as name,
    path, size, hash value, and last modified date.

    Example usage:
    \b
    # Basic usage - generates MD5 hashes for all files
    hashreport scan /path/to/directory -o report.csv

    \b
    # Use SHA256 and filter by size
    hashreport scan /path/to/directory -a sha256 --min-size 1MB --max-size 1GB

    \b
    # Filter by file patterns and email the report
    hashreport scan /path/to/directory --include "*.pdf" --email user@example.com
    """
    pass


@cli.command()
@click.argument("directory", type=click.Path(exists=True, file_okay=False))
@click.option("-o", "--output", type=click.Path(), help="Output file path or directory")
@click.option("-a", "--algorithm", default="md5", help="Hash algorithm to use")
@click.option(
    "-f",
    "--format",
    "output_format",
    default="csv",
    help="Output format (csv, json)",
)
@click.option(
    "--min-size", callback=validate_size, help="Minimum file size (e.g., 1MB)"
)
@click.option(
    "--max-size", callback=validate_size, help="Maximum file size (e.g., 1GB)"
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
def scan(
    directory: str,
    output: Optional[str],
    algorithm: str,
    output_format: str,
    min_size: Optional[str],
    max_size: Optional[str],
    include: Optional[List[str]],
    exclude: Optional[List[str]],
    regex: bool,
    limit: Optional[int],
    email: Optional[str],
    smtp_host: Optional[str],
    smtp_port: int,
    smtp_user: Optional[str],
    smtp_password: Optional[str],
    test_email: bool,
):
    """
    Scan directory and generate hash report.

    DIRECTORY is the path to scan for files.
    """
    try:
        # Set default output path if none provided
        if not output:
            output = os.path.join(os.getcwd(), f"hashreport.{output_format}")
        walk_directory_and_log(directory, output, algorithm=algorithm)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        raise click.Abort()


@cli.command()
def algorithms():
    """Show available hash algorithms."""
    show_available_options()


if __name__ == "__main__":
    cli()
