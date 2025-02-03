"""Handler for generating file lists."""

import os
from datetime import datetime
from pathlib import Path

import click

from hashreport.config import get_config
from hashreport.utils.progress_bar import ProgressBar
from hashreport.utils.scanner import count_files

config = get_config()


def get_filelist_filename(output_path: str) -> str:
    """Generate filelist filename with timestamp.

    Args:
        output_path: Base output path
    """
    timestamp = datetime.now().strftime(config.timestamp_format)
    path = Path(output_path)

    # If path is a directory, create new timestamped file
    if path.is_dir():
        return str(path / f"filelist_{timestamp}.txt")

    # For explicit paths, replace extension with .txt
    return str(path.with_suffix(".txt"))


def list_files_in_directory(
    directory: str,
    output_file: str,
    recursive: bool = True,
) -> None:
    """List files in a directory and log to a .txt file."""
    directory = Path(directory)
    output_file = Path(get_filelist_filename(output_file))

    success = False

    try:
        total_files = count_files(directory, recursive)
        progress_bar = ProgressBar(total=total_files)

        try:
            files_to_process = [
                os.path.join(root, file_name)
                for root, dirs, files in os.walk(directory)
                if recursive or not dirs.clear()
                for file_name in files
            ]

            with output_file.open("w", encoding="utf-8") as f:
                for file_path in files_to_process:
                    f.write(f"{file_path}\n")
                    progress_bar.update(1)

            success = True  # Mark as successful only if we get here

        except Exception as e:
            click.echo(f"Error writing file list: {e}", err=True)
            return

    except Exception as e:
        click.echo(f"Error during listing files: {e}", err=True)
    finally:
        progress_bar.finish()
        if success:
            click.echo(f"File list saved to: {output_file}")
