"""CSV report handler implementation."""

import csv
from typing import Any

from hashreport.reports.base import BaseReportHandler
from hashreport.utils.exceptions import ReportError
from hashreport.utils.type_defs import ReportData, ReportEntry, validate_report_data


class CSVReportHandler(BaseReportHandler):
    """Handler for CSV report files."""

    def read(self) -> ReportData:
        """Read the CSV report file.

        Returns:
            List of report entries

        Raises:
            ReportError: If there's an error reading the report
        """
        try:
            with self.filepath.open("r", newline="", encoding="utf-8") as f:
                data = list(csv.DictReader(f))
                return validate_report_data(data)
        except Exception as e:
            raise ReportError(f"Error reading CSV report: {e}")

    def write(self, data: ReportData, **kwargs: Any) -> None:
        """Write data to the CSV report file."""
        if not data:
            return

        try:
            validated_data = validate_report_data(data)
            self.validate_path()
            with self.filepath.open("w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=validated_data[0].keys())
                writer.writeheader()
                writer.writerows(validated_data)
        except OSError as e:
            raise ReportError(f"Error writing CSV report: {e}")

    def append(self, entry: ReportEntry) -> None:
        """Append a single entry to the CSV report.

        Args:
            entry: Report entry to append

        Raises:
            ReportError: If there's an error appending to the report
        """
        try:
            # Validate entry structure
            if not isinstance(entry, dict):
                raise ReportError("Entry must be a dictionary")

            self.validate_path()
            mode = "a" if self.filepath.exists() else "w"
            with self.filepath.open(mode, newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=entry.keys())
                if mode == "w":
                    writer.writeheader()
                writer.writerow(entry)
        except Exception as e:
            raise ReportError(f"Error appending to CSV report: {e}")
