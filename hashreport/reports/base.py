"""Base classes for report handlers."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, ClassVar, Dict, List, Union

from hashreport.utils.exceptions import ReportError


class BaseReportHandler(ABC):
    """Base class for report handlers."""

    REQUIRED_METHODS: ClassVar[set] = {"read", "write", "append"}

    def __init__(self, filepath: Union[str, Path]):
        """Initialize the report handler.

        Args:
            filepath: Path to the report file
        """
        self.filepath = Path(filepath)
        self._validate_interface()

    def _validate_interface(self) -> None:
        """Validate that all required methods are implemented."""
        missing = [
            method for method in self.REQUIRED_METHODS if not hasattr(self, method)
        ]
        if missing:
            raise NotImplementedError(
                f"Handler missing required methods: {', '.join(missing)}"
            )

    @abstractmethod
    def read(self) -> List[Dict[str, Any]]:
        """Read the report file.

        Returns:
            List of report entries

        Raises:
            ReportError: If there's an error reading the report
        """
        pass

    @abstractmethod
    def write(self, data: List[Dict[str, Any]], **kwargs: Any) -> None:
        """Write data to the report file.

        Args:
            data: List of report entries to write
            **kwargs: Additional options for the writer

        Raises:
            ReportError: If there's an error writing the report
        """
        pass

    @abstractmethod
    def append(self, entry: Dict[str, Any]) -> None:
        """Append a single entry to the report.

        Args:
            entry: Report entry to append

        Raises:
            ReportError: If there's an error appending to the report
        """
        pass

    def validate_path(self) -> None:
        """Validate and prepare the report filepath.

        Raises:
            ReportError: If there's an issue with the filepath
        """
        try:
            self.filepath.parent.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            raise ReportError(f"Failed to create directory: {e}")
