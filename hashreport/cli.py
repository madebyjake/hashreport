"""Command line interface for hashreport."""

import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from typing import List, Optional

import click
from rich.console import Console

from hashreport.const import global_const
from hashreport.reports.csv_handler import CSVReportHandler
from hashreport.reports.json_handler import JSONReportHandler
from hashreport.utils.email_sender import EmailSender
from hashreport.utils.filters import should_process_file
from hashreport.utils.hasher import calculate_hash, show_available_options
from hashreport.utils.progress_bar import ProgressBar
from hashreport.utils.viewer import ReportViewer

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
    "--format",
    type=click.Choice(["csv", "json"]),
    default="csv",
    help="Output format (default: csv)",
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
    format: str,
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
    if test_email and email:
        # Test email configuration
        email_sender = EmailSender(smtp_host, smtp_port, smtp_user, smtp_password)
        if email_sender.test_connection():
            click.echo("Email configuration test successful!")
        return

    # Generate timestamped filename
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    default_filename = f"hashreport-{timestamp}.{format}"

    # Set output path
    if not output:
        output = default_filename
    elif os.path.isdir(output):
        output = os.path.join(output, default_filename)
    elif not output.lower().endswith(f".{format}"):
        output = f"{output}.{format}"

    # Create output directory if it doesn't exist
    output_dir = os.path.dirname(output) or "."
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Initialize appropriate report handler
    handler = (
        JSONReportHandler(output) if format == "json" else CSVReportHandler(output)
    )

    # Process files
    results = []
    futures = []
    max_workers = os.cpu_count() or 4  # Default to 4 if cpu_count returns None
    total_files = sum(len(files) for _, _, files in os.walk(directory))
    progress_bar = ProgressBar(total=total_files)

    try:
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # First, collect all files that need processing
            files_to_process = []
            for root, _, files in os.walk(directory):
                for filename in files:
                    filepath = os.path.join(root, filename)
                    if should_process_file(
                        filepath, min_size, max_size, include, exclude, regex
                    ):
                        files_to_process.append(filepath)
                        if limit and len(files_to_process) >= limit:
                            break
                if limit and len(files_to_process) >= limit:
                    break

            # Submit all files for parallel processing
            futures = [
                executor.submit(calculate_hash, filepath, algorithm)
                for filepath in files_to_process
            ]

            # Process results as they complete
            for future in as_completed(futures):
                try:
                    file_data = future.result()
                    if file_data["Hash"]:
                        results.append(file_data)
                    progress_bar.update()
                except Exception as e:
                    click.echo(f"Error processing file: {e}", err=True)

    except Exception as e:
        click.echo(f"Error processing files: {e}", err=True)
        return

    progress_bar.finish()

    # Write report
    try:
        handler.write_report(results)
        click.echo(f"\nReport generated: {output}")

        # Send email if configured
        if email:
            email_sender = EmailSender(smtp_host, smtp_port, smtp_user, smtp_password)
            if email_sender.send_report(
                smtp_user or "hashreport@localhost",
                email,
                "Hash Report Complete",
                f"Hash report for {directory} is attached.",
                output,
                handler.get_mime_type(),
            ):
                click.echo("Report sent via email successfully!")
            else:
                click.echo("Failed to send email report.", err=True)

    except Exception as e:
        click.echo(f"Error writing report: {e}", err=True)


@cli.command()
def algorithms():
    """Show available hash algorithms."""
    show_available_options()


@cli.command()
@click.argument("report", type=click.Path(exists=True, dir_okay=False))
def view(report: str):
    """
    View a hash report in an interactive format.

    REPORT is the path to the report file to view.
    """
    try:
        viewer = ReportViewer(report)
        viewer.display_report()
    except Exception as e:
        click.echo(f"Error viewing report: {e}", err=True)


if __name__ == "__main__":
    cli()
