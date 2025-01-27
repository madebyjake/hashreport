"""JSON report handler implementation."""

import json
from typing import Any, Dict, List

from hashreport.reports.base import BaseReportHandler
from hashreport.utils.exceptions import ReportError


class JSONReportHandler(BaseReportHandler):
    """Handler for JSON report files."""

    def read(self) -> List[Dict[str, Any]]:
        """Read the JSON report file.

        Returns:
            List of report entries

        Raises:
            ReportError: If there's an error reading the report
        """
        try:
            with self.filepath.open("r", encoding="utf-8") as f:
                data = json.load(f)
                return data if isinstance(data, list) else [data]
        except Exception as e:
            raise ReportError(f"Error reading JSON report: {e}")

    def write(self, data: List[Dict[str, Any]], **kwargs: Any) -> None:
        """Write data to the JSON report file.

        Args:
            data: List of report entries to write
            **kwargs: Additional JSON dump options

        Raises:
            ReportError: If there's an error writing the report
        """
        if not isinstance(data, list):
            raise ReportError("Data must be a list of dictionaries")

        try:
            self.validate_path()
            with self.filepath.open("w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, **kwargs)
        except OSError as e:
            raise ReportError(f"Error writing JSON report: {e}")

    def append(self, entry: Dict[str, Any]) -> None:
        """Append a single entry to the JSON report.

        Args:
            entry: Report entry to append

        Raises:
            ReportError: If there's an error appending to the report
        """
        try:
            existing_data = []
            if self.filepath.exists():
                existing_data = self.read()

            existing_data.append(entry)
            self.write(existing_data)
        except Exception as e:
            raise ReportError(f"Error appending to JSON report: {e}")
