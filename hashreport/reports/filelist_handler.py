"""Handler for generating file lists."""

import os
from pathlib import Path

import click

from hashreport.config import get_config
from hashreport.utils.progress_bar import ProgressBar
from hashreport.utils.scanner import count_files

config = get_config()


def get_filelist_filename(output_path: str) -> str:
    """Get the output filename for the filelist.

    Args:
        output_path: The output directory or file path

    Returns:
        The full path to the output file
    """
    output = Path(output_path)
    if output.is_dir():
        return str(output / "filelist.txt")
    return str(output)


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
