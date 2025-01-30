"""CLI module for hashreport."""

import os
from typing import List

import click
from rich.console import Console

from hashreport.config import get_config
from hashreport.reports.filelist_handler import (
    get_filelist_filename,
    list_files_in_directory,
)
from hashreport.utils.hasher import show_available_options
from hashreport.utils.scanner import get_report_filename, walk_directory_and_log

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
        click.echo(f"Error: {e}", err=True)
        raise click.Abort()


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
        click.echo(f"Error: {e}", err=True)
        raise click.Abort()


cli.add_command(filelist)


@cli.command()
def algorithms():
    """Show available hash algorithms."""
    show_available_options()


if __name__ == "__main__":
    cli()
