"""Provides functions to scan directories, calculate hashes, and log results."""

import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple, Union, cast

import click

from hashreport.config import get_config
from hashreport.reports.base import BaseReportHandler
from hashreport.reports.csv_handler import CSVReportHandler
from hashreport.reports.json_handler import JSONReportHandler
from hashreport.utils.conversions import format_size, parse_size_string
from hashreport.utils.exceptions import HashReportError
from hashreport.utils.filters import should_process_file as filter_should_process_file
from hashreport.utils.hasher import calculate_hash
from hashreport.utils.progress_bar import ProgressBar
from hashreport.utils.type_defs import ReportData

logger = logging.getLogger(__name__)

config = get_config()


def get_report_handlers(filenames: List[str]) -> List[BaseReportHandler]:
    """Get report handlers for the given filenames.

    Args:
        filenames: List of output file paths

    Returns:
        List of appropriate report handlers
    """
    handlers: List[BaseReportHandler] = []
    for filename in filenames:
        path = Path(filename)
        handler: BaseReportHandler
        if path.suffix.lower() == ".csv":
            handler = CSVReportHandler(path)
        elif path.suffix.lower() == ".json":
            handler = JSONReportHandler(path)
        else:
            raise HashReportError(f"Unsupported file format: {path.suffix}")
        handlers.append(handler)
    return cast(List[BaseReportHandler], handlers)


def get_report_filename(
    output_path: str,
    output_format: Optional[str] = None,
    prefix: str = "hashreport",
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


def _convert_scanner_params_to_filter_params(
    exclude_paths: Optional[Set[str]] = None,
    file_extension: Optional[str] = None,
    file_names: Optional[Set[str]] = None,
    min_size: Optional[str] = None,
    max_size: Optional[str] = None,
    include: Optional[Tuple[str, ...]] = None,
    exclude: Optional[Tuple[str, ...]] = None,
    regex: bool = False,
) -> Dict[str, Any]:
    """Convert scanner parameters to filter parameters."""
    # Convert size strings to bytes
    min_size_bytes: Optional[int] = None
    max_size_bytes: Optional[int] = None
    if min_size:
        min_size_bytes = parse_size_string(min_size)
    if max_size:
        max_size_bytes = parse_size_string(max_size)

    # Convert include/exclude tuples to lists
    include_patterns = list(include) if include else None
    exclude_patterns = list(exclude) if exclude else None

    # Add file extension to include patterns if specified
    if file_extension:
        if include_patterns is None:
            include_patterns = []
        include_patterns.append(f"*{file_extension}")

    # Add specific file names to include patterns if specified
    if file_names:
        if include_patterns is None:
            include_patterns = []
        include_patterns.extend(file_names)

    # Handle exclude_paths by adding them to exclude_patterns
    if exclude_paths:
        if exclude_patterns is None:
            exclude_patterns = []
        # Convert full paths to filename patterns for exclusion
        for path in exclude_paths:
            filename = os.path.basename(path)
            exclude_patterns.append(filename)

    return {
        "include_patterns": include_patterns,
        "exclude_patterns": exclude_patterns,
        "use_regex": regex,
        "min_size": min_size_bytes,
        "max_size": max_size_bytes,
    }


def count_files(directory: Path, recursive: bool, **filter_kwargs) -> int:
    """Count files matching filter criteria."""
    # Convert old-style parameters to new filter parameters
    converted_params = _convert_scanner_params_to_filter_params(**filter_kwargs)

    total = 0
    for root, dirs, files in os.walk(directory):
        if not recursive:
            dirs[:] = []
        for file_name in files:
            file_path = os.path.join(root, file_name)
            if filter_should_process_file(file_path, **converted_params):
                total += 1
    return total


def collect_files_to_list(
    directory: str,
    recursive: bool = True,
    limit: Optional[int] = None,
    include: Optional[Tuple[str, ...]] = None,
    exclude: Optional[Tuple[str, ...]] = None,
    regex: bool = False,
    min_size: Optional[str] = None,
    max_size: Optional[str] = None,
) -> List[str]:
    """Collect file paths matching filter criteria (for filelist and similar use).

    Args:
        directory: Directory to walk
        recursive: Whether to recurse into subdirectories
        limit: Maximum number of files to return (None = no limit)
        include: Tuple of include patterns (glob or regex)
        exclude: Tuple of exclude patterns (glob or regex)
        regex: Whether include/exclude patterns are regex
        min_size: Minimum file size string (e.g. 1MB)
        max_size: Maximum file size string (e.g. 1GB)

    Returns:
        List of file paths matching the filters
    """
    filter_params = _convert_scanner_params_to_filter_params(
        include=include,
        exclude=exclude,
        regex=regex,
        min_size=min_size,
        max_size=max_size,
    )
    return _collect_files_to_process(
        directory,
        None,
        filter_params,
        limit=limit,
        recursive=recursive,
    )


def _collect_files_to_process(
    directory: str,
    specific_files: Optional[Set[str]],
    filter_params: Dict[str, Any],
    limit: Optional[int] = None,
    recursive: bool = True,
) -> List[str]:
    """Collect files to process based on specific files or directory walk."""
    if specific_files:
        return [
            f for f in specific_files if filter_should_process_file(f, **filter_params)
        ]
    files_to_process: List[str] = []
    directory_path = Path(directory)
    for root, dirs, files in os.walk(directory_path):
        if not recursive:
            dirs[:] = []
        for file_name in files:
            file_path = os.path.join(root, file_name)
            if filter_should_process_file(file_path, **filter_params):
                files_to_process.append(file_path)
                if limit and len(files_to_process) >= limit:
                    break
        if limit and len(files_to_process) >= limit:
            break
    return files_to_process


def _process_single_batch(
    batch: List[str], algorithm: str, progress_bar: ProgressBar
) -> List[Dict[str, str]]:
    """Process a single batch of files and return results."""
    from hashreport.utils.thread_pool import ThreadPoolManager

    results = []
    with ThreadPoolManager(
        initial_workers=config.max_workers,
        progress_bar=None,  # Don't let thread pool handle progress
    ) as pool:
        # Update progress bar with first file in batch
        if batch:
            progress_bar.update(0, file_name=os.path.basename(batch[0]))

        # Process the batch
        hash_results = pool.process_items(batch, lambda x: calculate_hash(x, algorithm))

        # Handle results and update progress
        for result in hash_results:
            path, hash_val, mod_time = result
            if hash_val:  # Only add if hash was successful
                file_path = Path(path)
                file_size = os.path.getsize(path)
                results.append(
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
                # Update progress bar with current file name
                progress_bar.update(1, file_name=file_path.name)

    return results


def _process_file_batches(
    files_to_process: List[str], algorithm: str, progress_bar: ProgressBar
) -> List[Dict[str, str]]:
    """Process files in batches and return all results."""
    final_results = []

    # Process files in batches
    batch_size = min(100, len(files_to_process))
    for i in range(0, len(files_to_process), batch_size):
        batch = files_to_process[i : i + batch_size]
        batch_results = _process_single_batch(batch, algorithm, progress_bar)
        final_results.extend(batch_results)

    return final_results


def _write_scan_results(
    handlers: List[BaseReportHandler],
    final_results: List[Dict[str, str]],
    output_files: Union[str, List[str]],
) -> List[str]:
    """Write scan results to all handlers and return report paths."""
    output_list: List[str] = cast(
        List[str],
        [output_files] if isinstance(output_files, str) else output_files,
    )
    reports: List[str] = []
    for handler in handlers:
        if not hasattr(handler, "write"):
            click.echo(
                f"Error: Handler {type(handler).__name__} missing write method",
                err=True,
            )
            return []
        logger.debug(f"Writing {len(final_results)} results to {output_list}")
        handler.write(cast(ReportData, final_results))
        reports.append(str(handler.filepath))
    return reports


def walk_directory_and_log(
    directory: str,
    output_files: Union[str, List[str]],
    algorithm: Optional[str] = None,
    exclude_paths: Optional[Set[str]] = None,
    file_extension: Optional[str] = None,
    file_names: Optional[Set[str]] = None,
    limit: Optional[int] = None,
    specific_files: Optional[Set[str]] = None,
    min_size: Optional[str] = None,
    max_size: Optional[str] = None,
    include: Optional[Tuple[str, ...]] = None,
    exclude: Optional[Tuple[str, ...]] = None,
    regex: bool = False,
    recursive: bool = True,
) -> None:
    """Walk through a directory, calculate hashes, and log to report."""
    algorithm = algorithm or config.default_algorithm
    success = False
    reports: List[str] = []
    progress_bar: Optional[ProgressBar] = None

    try:
        output_list = (
            [output_files] if isinstance(output_files, str) else list(output_files)
        )
        handlers = get_report_handlers(output_list)
        logger.debug(f"Using handlers: {[type(h).__name__ for h in handlers]}")

        filter_params = _convert_scanner_params_to_filter_params(
            exclude_paths=exclude_paths,
            file_extension=file_extension,
            file_names=file_names,
            min_size=min_size,
            max_size=max_size,
            include=include,
            exclude=exclude,
            regex=regex,
        )

        files_to_process = _collect_files_to_process(
            directory=directory,
            specific_files=specific_files,
            filter_params=filter_params,
            limit=limit,
            recursive=recursive,
        )

        pbar: ProgressBar = ProgressBar(
            total=len(files_to_process),
            show_file_names=config.progress["show_file_names"],
        )
        progress_bar = pbar

        final_results = _process_file_batches(files_to_process, algorithm, pbar)

        reports = _write_scan_results(
            handlers,
            final_results,
            cast(Union[str, List[str]], output_files),
        )
        success = True
        logger.debug("Successfully wrote results")

    except AttributeError as e:
        click.echo(f"Error: Invalid handler interface - {e}", err=True)
        return
    except Exception as e:
        logger.exception("Error during scanning")
        click.echo(f"Error during scanning: {e}", err=True)
        return
    finally:
        if progress_bar is not None:
            progress_bar.finish()
        if success:
            if len(reports) == 1:
                click.echo(f"Report saved to: {reports[0]}")
            else:
                click.echo("Reports saved to:")
                for report in reports:
                    click.echo(f"  - {report}")
