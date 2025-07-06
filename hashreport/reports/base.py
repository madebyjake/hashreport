"""Base classes for report handlers."""

from pathlib import Path
from typing import Any, ClassVar

from hashreport.utils.exceptions import ReportError
from hashreport.utils.type_defs import (
    FilePath,
    ReportData,
    ReportEntry,
    validate_file_path,
)


class BaseReportHandler:
    """Base class for report handlers."""

    REQUIRED_METHODS: ClassVar[set] = {"read", "write", "append"}

    def __init__(self, filepath: FilePath):
        """Initialize the report handler.

        Args:
            filepath: Path to the report file
        """
        self.filepath = Path(validate_file_path(filepath))
        self._validate_interface()

    def _validate_interface(self) -> None:
        """Validate that all required methods are implemented."""
        missing = []
        for m in self.REQUIRED_METHODS:
            method = getattr(self, m, None)
            base_method = getattr(BaseReportHandler, m, None)
            if method is None or getattr(method, "__code__", None) == getattr(
                base_method, "__code__", None
            ):
                missing.append(m)

        if missing:
            raise NotImplementedError(
                f"Handler missing required methods: {', '.join(missing)}"
            )

    def read(self) -> ReportData:
        """Read the report file.

        Returns:
            List of report entries

        Raises:
            ReportError: If there's an error reading the report
        """
        raise NotImplementedError("Subclasses must override 'read'.")

    def write(self, data: ReportData, **kwargs: Any) -> None:
        """Write data to the report file.

        Args:
            data: List of report entries to write
            **kwargs: Additional options for the writer

        Raises:
            ReportError: If there's an error writing the report
        """
        raise NotImplementedError("Subclasses must override 'write'.")

    def append(self, entry: ReportEntry) -> None:
        """Append a single entry to the report.

        Args:
            entry: Report entry to append

        Raises:
            ReportError: If there's an error appending to the report
        """
        raise NotImplementedError("Subclasses must override 'append'.")

    def validate_path(self) -> None:
        """Validate and prepare the report filepath.

        Raises:
            ReportError: If there's an issue with the filepath
        """
        try:
            parent = self.filepath.parent
            if not parent.exists():
                try:
                    parent.mkdir(parents=True, exist_ok=True)
                except OSError as e:
                    raise ReportError(f"Failed to create directory '{parent}': {e}")
            elif not parent.is_dir():
                raise ReportError(f"Path exists but is not a directory: {parent}")
        except Exception as e:
            raise ReportError(f"Failed to validate path: {e}")
