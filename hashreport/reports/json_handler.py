"""JSON report handler for reading and writing JSON report files.

This module provides functionality for reading, writing, and appending to JSON report files.
It includes validation of report data structure and error handling.

Example:
    >>> handler = JSONReportHandler("report.json")
    >>> handler.write([{"file": "test.txt", "hash": "abc123"}])
    >>> data = handler.read()
"""  # noqa: E501

import json
from typing import Any

from hashreport.reports.base import BaseReportHandler
from hashreport.utils.exceptions import ReportError
from hashreport.utils.type_defs import ReportData, ReportEntry, validate_report_data


class JSONReportError(ReportError):
    """Exception raised for JSON-specific report errors."""

    pass


class JSONReportHandler(BaseReportHandler):
    """Handler for JSON report files.

    This handler provides methods for reading, writing, and appending to JSON report files.
    It validates the data structure and ensures all entries have the required fields.

    Args:
        filepath: Path to the JSON report file
    """  # noqa: E501

    def _validate_data(self, data: Any) -> ReportData:
        """Validate report data structure.

        Args:
            data: Data to validate

        Returns:
            Validated list of report entries

        Raises:
            JSONReportError: If data structure is invalid
        """
        if not isinstance(data, (list, dict)):
            raise JSONReportError("Data must be a list or dictionary")

        if isinstance(data, dict):
            data = [data]

        for entry in data:
            if not isinstance(entry, dict):
                raise JSONReportError("Each entry must be a dictionary")

            # Handle both old and new field names
            if "file" not in entry and "File Path" not in entry:
                raise JSONReportError(
                    "Each entry must have a 'file' or 'File Path' field"
                )

            # Convert old field names to new format
            if "File Path" in entry:
                entry["file"] = entry.pop("File Path")
            if "File Name" in entry:
                entry["name"] = entry.pop("File Name")
            if "Hash Value" in entry:
                entry["hash"] = entry.pop("Hash Value")
            if "Hash Algorithm" in entry:
                entry["algorithm"] = entry.pop("Hash Algorithm")
            if "Last Modified Date" in entry:
                entry["modified"] = entry.pop("Last Modified Date")
            if "Created Date" in entry:
                entry["created"] = entry.pop("Created Date")
            if "Size" in entry:
                entry["size"] = entry.pop("Size")

        return validate_report_data(data)

    def read(self) -> ReportData:
        """Read data from the JSON report file.

        Returns:
            List of report entries

        Raises:
            JSONReportError: If there's an error reading the report
        """
        try:
            if not self.filepath.exists():
                return []

            with self.filepath.open("r", encoding="utf-8") as f:
                data = json.load(f)
                return self._validate_data(data)
        except json.JSONDecodeError as e:
            raise JSONReportError(f"Invalid JSON format: {e}")
        except OSError as e:
            raise JSONReportError(f"Error reading JSON report: {e}")
        except Exception as e:
            raise JSONReportError(f"Error processing report data: {e}")

    def write(self, data: ReportData, **kwargs: Any) -> None:
        """Write data to the JSON report file.

        Args:
            data: List of report entries to write
            **kwargs: Additional JSON dump options (e.g., indent, sort_keys)

        Raises:
            JSONReportError: If there's an error writing or validating the report
        """
        try:
            validated_data = self._validate_data(data)
            self.validate_path()
            with self.filepath.open("w", encoding="utf-8") as f:
                json.dump(validated_data, f, indent=2, **kwargs)
        except OSError as e:
            raise JSONReportError(f"Error writing JSON report: {e}")
        except Exception as e:
            raise JSONReportError(f"Error processing report data: {e}")

    def append(self, entry: ReportEntry) -> None:
        """Append a single entry to the JSON report.

        This method reads the existing report, appends the new entry, and writes back
        the complete report. For large files, consider using append_streaming() instead.

        Args:
            entry: Report entry to append

        Raises:
            JSONReportError: If there's an error appending to the report
        """
        try:
            existing_data = []
            if self.filepath.exists():
                existing_data = self.read()

            validated_entry = self._validate_data(entry)[0]
            existing_data.append(validated_entry)
            self.write(existing_data)
        except Exception as e:
            raise JSONReportError(f"Error appending to JSON report: {e}")

    def append_streaming(self, entry: ReportEntry) -> None:
        """Append a single entry to the JSON report using streaming.

        This method is optimized for large files by using streaming to append entries
        without reading the entire file into memory.

        Args:
            entry: Report entry to append

        Raises:
            JSONReportError: If there's an error appending to the report
        """
        try:
            validated_entry = self._validate_data(entry)[0]
            self.validate_path()

            if not self.filepath.exists():
                # If file doesn't exist, create it with the first entry
                with self.filepath.open("w", encoding="utf-8") as f:
                    json.dump([validated_entry], f, indent=2)
            else:
                # Read the last character of the file
                with self.filepath.open("rb+") as f:
                    f.seek(0, 2)  # Seek to end of file
                    f.seek(-1, 2)  # Go back one character
                    last_char = f.read(1).decode("utf-8")

                    # If the last character is ']', remove it
                    if last_char == "]":
                        f.seek(-1, 2)
                        f.truncate()
                        f.write(b",\n  ")  # Add comma and newline
                    else:
                        f.write(b"[\n  ")  # Start new array

                    # Write the new entry
                    json.dump(validated_entry, f, indent=2)
                    f.write(b"\n]")  # Close the array
        except OSError as e:
            raise JSONReportError(f"Error appending to JSON report: {e}")
        except Exception as e:
            raise JSONReportError(f"Error processing report data: {e}")
