"""Provides functions to scan directories, calculate hashes, and log results."""

import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set, Union

import click

from hashreport.config import get_config
from hashreport.reports.base import BaseReportHandler
from hashreport.reports.csv_handler import CSVReportHandler
from hashreport.reports.json_handler import JSONReportHandler
from hashreport.utils.conversions import format_size
from hashreport.utils.hasher import calculate_hash
from hashreport.utils.progress_bar import ProgressBar
from hashreport.utils.thread_pool import ThreadPoolManager

logger = logging.getLogger(__name__)

config = get_config()


def get_report_handlers(filenames: List[str]) -> List[BaseReportHandler]:
    """Get report handlers for the given filenames.

    Args:
        filenames: List of output file paths

    Returns:
        List of appropriate report handlers
    """
    handlers = []
    for filename in filenames:
        # Use strict JSON checking
        if filename.lower().endswith(".json"):
            handlers.append(JSONReportHandler(filename))
        else:
            handlers.append(CSVReportHandler(filename))
    return handlers


def get_report_filename(
    output_path: str, output_format: str = None, prefix: str = "hashreport"
) -> str:
    """Generate report filename with timestamp.

    Args:
        output_path: Base output path
        output_format: Optional format override (json/csv)
        prefix: Optional prefix for the filename
    """
    timestamp = datetime.now().strftime(config.timestamp_format)
    path = Path(output_path)

    # Force format extension
    ext = f".{output_format.lower()}" if output_format else ".csv"

    # If path is a directory, create new timestamped file
    if path.is_dir():
        return str(path / f"{prefix}_{timestamp}{ext}")

    # For explicit paths, replace extension with format
    return str(path.with_suffix(ext))


def should_process_file(
    file_path: str,
    exclude_paths: Optional[Set[str]] = None,
    file_extension: Optional[str] = None,
    file_names: Optional[Set[str]] = None,
    min_size: Optional[str] = None,
    max_size: Optional[str] = None,
) -> bool:
    """Check if a file should be processed based on filters."""
    if exclude_paths and file_path in exclude_paths:
        return False

    file_name = os.path.basename(file_path)
    if file_extension and not file_name.endswith(file_extension):
        return False
    if file_names and file_name not in file_names:
        return False

    # Size checks
    try:
        size = os.path.getsize(file_path)
        if min_size and size < min_size:
            return False
        if max_size and size > max_size:
            return False
    except OSError:
        return False

    return True


def count_files(directory: Path, recursive: bool, **filter_kwargs) -> int:
    """Count files matching filter criteria."""
    total = 0
    for root, dirs, files in os.walk(directory):
        if not recursive:
            dirs[:] = []
        for file_name in files:
            file_path = os.path.join(root, file_name)
            if should_process_file(file_path, **filter_kwargs):
                total += 1
    return total


def walk_directory_and_log(
    directory: str,
    output_files: Union[str, List[str]],
    algorithm: str = None,
    exclude_paths: Optional[Set[str]] = None,
    file_extension: Optional[str] = None,
    file_names: Optional[Set[str]] = None,
    limit: Optional[int] = None,
    specific_files: Optional[Set[str]] = None,
    min_size: Optional[str] = None,
    max_size: Optional[str] = None,
    include: Optional[tuple] = None,
    exclude: Optional[tuple] = None,
    regex: bool = False,
    recursive: bool = True,
) -> None:
    """Walk through a directory, calculate hashes, and log to report."""
    algorithm = algorithm or config.default_algorithm
    directory = Path(directory)

    # Handle both string and list inputs for output_files
    if isinstance(output_files, str):
        output_files = [output_files]

    # Use the extensions as provided, no modification
    success = False

    try:
        handlers = get_report_handlers(output_files)
        logger.debug(
            f"Using handlers: {[type(handler).__name__ for handler in handlers]}"
        )
        final_results: List[Dict[str, str]] = []

        # Count only files that match filters
        total_files = count_files(
            directory,
            recursive,
            exclude_paths=exclude_paths,
            file_extension=file_extension,
            file_names=file_names,
            min_size=min_size,
            max_size=max_size,
        )
        progress_bar = ProgressBar(total=total_files)

        try:
            with ThreadPoolManager(
                initial_workers=config.max_workers, progress_bar=progress_bar
            ) as pool:
                if specific_files:
                    files_to_process = [
                        f
                        for f in specific_files
                        if should_process_file(
                            f,
                            exclude_paths=exclude_paths,
                            file_extension=file_extension,
                            file_names=file_names,
                            min_size=min_size,
                            max_size=max_size,
                        )
                    ]
                    results = pool.process_items(
                        files_to_process, lambda x: calculate_hash(x, algorithm)
                    )
                else:
                    files_to_process = [
                        os.path.join(root, file_name)
                        for root, dirs, files in os.walk(directory)
                        if recursive or not dirs.clear()
                        for file_name in files
                        if should_process_file(
                            os.path.join(root, file_name),
                            exclude_paths=exclude_paths,
                            file_extension=file_extension,
                            file_names=file_names,
                            min_size=min_size,
                            max_size=max_size,
                        )
                    ][:limit]
                    results = pool.process_items(
                        files_to_process, lambda x: calculate_hash(x, algorithm)
                    )

                for result in results:
                    path, hash_val, mod_time = result
                    if hash_val:  # Only add if hash was successful
                        file_path = Path(path)
                        file_size = os.path.getsize(path)
                        final_results.append(
                            {
                                "File Name": file_path.name,
                                "File Path": str(file_path),
                                "Size": format_size(file_size),
                                "Hash Algorithm": algorithm,
                                "Hash Value": hash_val,
                                "Last Modified Date": mod_time,
                                "Created Date": datetime.fromtimestamp(
                                    os.path.getctime(path)
                                ).strftime("%Y-%m-%d %H:%M:%S"),
                            }
                        )

            reports = []
            for handler in handlers:
                if not hasattr(handler, "write"):
                    click.echo(
                        f"Error: Handler {type(handler).__name__} missing write method",
                        err=True,
                    )
                    return
                logger.debug(f"Writing {len(final_results)} results to {output_files}")
                handler.write(final_results)
                reports.append(str(handler.filepath))
            success = True  # Mark as successful only if we get here
            logger.debug("Successfully wrote results")

        except AttributeError as e:
            click.echo(f"Error: Invalid handler interface - {e}", err=True)
            return
        except Exception as e:
            logger.exception("Error writing results")
            click.echo(f"Error writing report: {e}", err=True)
            return

    except Exception as e:
        logger.exception("Error during scanning")
        click.echo(f"Error during scanning: {e}", err=True)
    finally:
        progress_bar.finish()
        if success:  # Only show paths if everything succeeded
            if len(reports) == 1:
                click.echo(f"Report saved to: {reports[0]}")
            else:
                click.echo("Reports saved to:")
                for report in reports:
                    click.echo(f"  - {report}")
