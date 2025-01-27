"""CSV report handler implementation."""

import csv
from typing import Any, Dict, List

from hashreport.reports.base import BaseReportHandler
from hashreport.utils.exceptions import ReportError


class CSVReportHandler(BaseReportHandler):
    """Handler for CSV report files."""

    def read(self) -> List[Dict[str, Any]]:
        """Read the CSV report file.

        Returns:
            List of report entries

        Raises:
            ReportError: If there's an error reading the report
        """
        try:
            with self.filepath.open("r", newline="", encoding="utf-8") as f:
                return list(csv.DictReader(f))
        except Exception as e:
            raise ReportError(f"Error reading CSV report: {e}")

    def write(self, data: List[Dict[str, Any]], **kwargs: Any) -> None:
        """Write data to the CSV report file."""
        if not data:
            return

        try:
            self.validate_path()
            with self.filepath.open("w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=data[0].keys())
                writer.writeheader()
                writer.writerows(data)
        except OSError as e:
            raise ReportError(f"Error writing CSV report: {e}")

    def append(self, entry: Dict[str, Any]) -> None:
        """Append a single entry to the CSV report.

        Args:
            entry: Report entry to append

        Raises:
            ReportError: If there's an error appending to the report
        """
        try:
            self.validate_path()
            mode = "a" if self.filepath.exists() else "w"
            with self.filepath.open(mode, newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=entry.keys())
                if mode == "w":
                    writer.writeheader()
                writer.writerow(entry)
        except Exception as e:
            raise ReportError(f"Error appending to CSV report: {e}")
