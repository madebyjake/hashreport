"""Report viewer and comparison functionality."""

from pathlib import Path
from typing import Dict, List, Optional, Union

from rich import box
from rich.console import Console
from rich.table import Table
from rich.text import Text

from hashreport.reports.base import BaseReportHandler
from hashreport.reports.compare_handler import (
    ChangeType,
    CompareReportHandler,
    FileChange,
)
from hashreport.reports.csv_handler import CSVReportHandler
from hashreport.reports.json_handler import JSONReportHandler
from hashreport.utils.exceptions import ReportError


class ReportViewer:
    """Report viewer and comparison functionality."""

    def __init__(self, console: Optional[Console] = None):
        """Initialize report viewer."""
        self.console = console or Console()
        self._supported_formats = {".csv": CSVReportHandler, ".json": JSONReportHandler}
        self._compare_handler = CompareReportHandler()

    def _get_handler(self, filepath: Union[str, Path]) -> BaseReportHandler:
        """Get appropriate handler for file type."""
        path = Path(filepath)
        handler_class = self._supported_formats.get(path.suffix.lower())
        if not handler_class:
            raise ReportError(f"Unsupported file format: {path.suffix}")
        return handler_class(path)

    def _render_table(self, data: List[Dict]) -> Table:
        """Create a formatted table from report data."""
        table = Table(
            show_header=True,
            box=box.MINIMAL_DOUBLE_HEAD,
            show_lines=True,  # Add lines between rows for readability
            pad_edge=True,  # Add padding around edges
            expand=True,  # Allow table to use full width
        )
        if data:
            # Add columns based on first entry
            for header in data[0].keys():
                # Auto-wrap text and set minimum/maximum widths
                table.add_column(
                    header,
                    overflow="fold",  # Wrap text that exceeds width
                    min_width=8,  # Minimum column width
                    max_width=80,  # Maximum column width
                    no_wrap=False,  # Allow text wrapping
                )

            # Add rows with wrapped content
            for entry in data:
                table.add_row(*[str(v) for v in entry.values()])

        return table

    def view_report(self, report: str, filter_text: Optional[str] = None) -> None:
        """View report contents with optional filtering.

        Args:
            report: Path to the report file
            filter_text: Optional filter pattern to apply
        """
        self.display_report(report, filter_text)

    def compare_reports(
        self, report1: str, report2: str, output: Optional[str] = None
    ) -> None:
        """Compare two reports and show differences.

        Args:
            report1: Path to the first report file
            report2: Path to the second report file
            output: Optional output directory for the comparison report
        """
        changes = self._compare_reports(report1, report2)

        # Display the comparison
        self.display_comparison(changes)

        # Save comparison report if output directory is provided
        if output:
            self.save_comparison(changes, output, report1, report2)

    def _compare_reports(self, report1: str, report2: str) -> List[FileChange]:
        """Compare two reports and identify differences."""
        old_data = self._get_handler(report1).read()
        new_data = self._get_handler(report2).read()
        return self._compare_handler.compare_reports(old_data, new_data)

    def save_comparison(
        self, changes: List[FileChange], output_dir: str, report1: str, report2: str
    ) -> None:
        """Save comparison results to a new report file."""
        output_file = self._compare_handler.get_output_filename(
            report1, report2, output_dir
        )
        data = self._compare_handler.format_changes_for_save(changes)
        handler = self._get_handler(output_file)
        handler.write(data)

    def display_report(self, filepath: str, filter_text: Optional[str] = None) -> None:
        """Display report contents with optional filtering and paging."""
        data = self._get_handler(filepath).read()

        if filter_text:
            filtered_data = []
            filter_lower = filter_text.lower()
            for entry in data:
                if any(filter_lower in str(v).lower() for v in entry.values()):
                    filtered_data.append(entry)
            data = filtered_data

        table = self._render_table(data)

        # Display using system pager with raw formatting for totals
        with self.console.pager():
            self.console.print(table)
            self.console.print("\nTotal entries:", len(data))

    def display_comparison(self, changes: List[FileChange]) -> None:
        """Display comparison results in a formatted table with paging."""
        table = Table(
            show_header=True,
            box=box.MINIMAL_DOUBLE_HEAD,
            show_lines=True,
            pad_edge=True,
            expand=True,
        )
        table.add_column("Change", min_width=8, max_width=12)
        table.add_column("File Name", min_width=20, max_width=60)
        table.add_column("Details", min_width=30, max_width=100, overflow="fold")
        table.add_column("Old Path", min_width=20, max_width=100, overflow="fold")
        table.add_column("New Path", min_width=20, max_width=100, overflow="fold")

        for change in changes:
            # Use bold text for change type
            change_type = Text(str(change.change_type), style="bold")

            if change.change_type == ChangeType.MODIFIED:
                details = (
                    f"[bold]Hash changed:[/bold] {change.old_hash} → {change.new_hash}"
                )
            elif change.change_type == ChangeType.MOVED:
                details = "[bold]File moved[/bold]"
            elif change.change_type == ChangeType.REMOVED:
                details = f"[bold]Old hash:[/bold] {change.old_hash}"
            else:  # ADDED
                details = f"[bold]New hash:[/bold] {change.new_hash}"

            table.add_row(
                change_type,
                change.path,
                details,
                change.old_path or "",
                change.new_path or "",
            )

        # Display using system pager with raw formatting for totals
        with self.console.pager():
            self.console.print(table)
            self.console.print("\nTotal changes:", len(changes))
