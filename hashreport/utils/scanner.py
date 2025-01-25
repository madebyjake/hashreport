"""Provides functions to scan directories, calculate hashes, and log results."""

import logging
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set

import click

from hashreport.reports.csv_handler import CSVReportHandler
from hashreport.reports.json_handler import JSONReportHandler
from hashreport.utils.conversions import format_size
from hashreport.utils.hasher import calculate_hash
from hashreport.utils.progress_bar import ProgressBar

logger = logging.getLogger(__name__)


def get_report_handler(file_path: str):
    """Get the appropriate report handler based on file extension."""
    logger.debug(f"Creating report handler for {file_path}")
    handler = (
        JSONReportHandler(file_path)
        if file_path.lower().endswith(".json")
        else CSVReportHandler(file_path)
    )
    logger.debug(f"Handler methods: {dir(handler)}")
    return handler


def get_report_filename(output_path: str) -> str:
    """Generate report filename with timestamp."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = Path(output_path)

    # If path is a directory, use CSV as default format
    if path.is_dir():
        return str(path / f"hashreport-{timestamp}.csv")

    # If path exists or has a suffix, use it as is
    if path.suffix or path.exists():
        return str(path)

    # Default to CSV if no extension is provided
    return str(path.with_suffix(".csv"))


def walk_directory_and_log(
    directory: str,
    output_path: str,
    algorithm: str = "md5",
    exclude_paths: Optional[Set[str]] = None,
    file_extension: Optional[str] = None,
    file_names: Optional[Set[str]] = None,
    limit: Optional[int] = None,
    specific_files: Optional[Set[str]] = None,
) -> None:
    """Walk through a directory, calculate hashes, and log to report."""
    directory = Path(directory)
    output_path = str(get_report_filename(output_path))
    success = False

    try:
        handler = get_report_handler(output_path)
        logger.debug(f"Using handler: {type(handler).__name__}")
        results: List[Dict[str, str]] = []

        total_files = (
            len(specific_files)
            if specific_files
            else sum(len(files) for _, _, files in os.walk(directory))
        )
        progress_bar = ProgressBar(total=total_files)

        try:
            max_workers = os.cpu_count()
            futures = []

            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                count = 0
                if specific_files:
                    for file_path in specific_files:
                        futures.append(
                            executor.submit(calculate_hash, file_path, algorithm)
                        )
                        count += 1
                        if limit and count >= limit:
                            break
                else:
                    for root, dirs, files in os.walk(directory):
                        if exclude_paths:
                            dirs[:] = [
                                d
                                for d in dirs
                                if os.path.join(root, d) not in exclude_paths
                            ]
                        for file_name in files:
                            full_path = os.path.join(root, file_name)
                            if exclude_paths and full_path in exclude_paths:
                                continue
                            if file_extension and not file_name.endswith(
                                file_extension
                            ):
                                continue
                            if file_names and file_name not in file_names:
                                continue
                            futures.append(
                                executor.submit(calculate_hash, full_path, algorithm)
                            )
                            count += 1
                            if limit and count >= limit:
                                break
                        if limit and count >= limit:
                            break

                for future in as_completed(futures):
                    try:
                        path, hash_val, mod_time = future.result()
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
                            progress_bar.update()
                    except ValueError as e:
                        logger.error(f"Error processing result: {e}")
                        continue

            if not hasattr(handler, "write"):
                click.echo(
                    f"Error: Handler {type(handler).__name__} missing write method",
                    err=True,
                )
                return
            logger.debug(f"Writing {len(results)} results to {output_path}")
            handler.write(results)
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
        if success:  # Only show output path if everything succeeded
            click.echo(f"Report saved to: {output_path}")
