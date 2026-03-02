"""Handler for generating file lists."""

from pathlib import Path
from typing import Optional, Tuple

import click

from hashreport.utils.progress_bar import ProgressBar
from hashreport.utils.scanner import collect_files_to_list


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
    include: Optional[Tuple[str, ...]] = None,
    exclude: Optional[Tuple[str, ...]] = None,
    regex: bool = False,
    min_size: Optional[str] = None,
    max_size: Optional[str] = None,
    limit: Optional[int] = None,
) -> None:
    """List directory files (optional filters) and write paths to a .txt file."""
    output_path = Path(get_filelist_filename(output_file))

    success = False
    progress_bar = None

    try:
        files_to_process = collect_files_to_list(
            str(directory),
            recursive=recursive,
            limit=limit,
            include=include,
            exclude=exclude,
            regex=regex,
            min_size=min_size,
            max_size=max_size,
        )
        total_files = len(files_to_process)
        progress_bar = ProgressBar(total=total_files)

        output_path.parent.mkdir(parents=True, exist_ok=True)
        with output_path.open("w", encoding="utf-8") as f:
            for file_path in files_to_process:
                f.write(f"{file_path}\n")
                progress_bar.update(1)

        success = True

    except Exception as e:
        click.echo(f"Error during listing files: {e}", err=True)
    finally:
        if progress_bar is not None:
            progress_bar.finish()
        if success:
            click.echo(f"File list saved to: {output_path}")
