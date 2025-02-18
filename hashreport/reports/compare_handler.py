"""Compare report handler module."""

from dataclasses import dataclass
from enum import Enum, auto
from pathlib import Path
from typing import Dict, List, Optional

from hashreport.utils.exceptions import ReportError


class CompareError(ReportError):
    """Base exception for comparison errors."""

    pass


class EmptyReportError(CompareError):
    """Exception raised when a report is empty."""

    pass


class ColumnNotFoundError(CompareError):
    """Exception raised when required column is not found."""

    pass


class ChangeType(Enum):
    """Types of changes between reports."""

    REMOVED = auto()
    ADDED = auto()
    MODIFIED = auto()
    MOVED = auto()

    def __str__(self) -> str:
        """Return lowercase string representation of change type."""
        return self.name.lower()


@dataclass
class FileChange:
    """Represents a change between two reports."""

    change_type: ChangeType
    path: str
    old_hash: Optional[str] = None
    new_hash: Optional[str] = None
    old_path: Optional[str] = None
    new_path: Optional[str] = None


class CompareReportHandler:
    """Handler for comparing and generating comparison reports."""

    def __init__(self):
        """Initialize report handler."""
        self._hash_columns = ["Hash", "Hash Value", "hash", "hash_value"]
        self._name_columns = ["File Name", "Filename", "Name", "file_name", "filename"]
        self._path_columns = ["File Path", "Path", "file_path", "path"]

    def _get_column_name(self, headers: List[str], possible_names: List[str]) -> str:
        """Find matching column name from possible variations."""
        for name in possible_names:
            if name in headers:
                return name
        raise ColumnNotFoundError(
            f"Could not find required column. Tried: {', '.join(possible_names)}"
        )

    def _get_file_name_and_path(self, entry: Dict[str, str]) -> tuple[str, str]:
        """Get file name and path from entry."""
        headers = entry.keys()
        name_col = self._get_column_name(headers, self._name_columns)
        try:
            path_col = self._get_column_name(headers, self._path_columns)
            return entry[name_col], entry[path_col]
        except ColumnNotFoundError:
            return entry[name_col], ""

    def compare_reports(
        self, old_data: List[Dict], new_data: List[Dict]
    ) -> List[FileChange]:
        """Compare two report datasets and identify differences."""
        if not old_data or not new_data:
            raise EmptyReportError("One or both reports are empty")

        headers = list(old_data[0].keys())
        hash_col = self._get_column_name(headers, self._hash_columns)

        # Build indexes using filenames
        old_index = {}
        new_index = {}

        for entry in old_data:
            name, path = self._get_file_name_and_path(entry)
            old_index[name] = {"entry": entry, "path": path}

        for entry in new_data:
            name, path = self._get_file_name_and_path(entry)
            new_index[name] = {"entry": entry, "path": path}

        changes = []

        # Check for removed and modified files
        for name, old_entry in old_index.items():
            if name not in new_index:
                changes.append(
                    FileChange(
                        change_type=ChangeType.REMOVED,
                        path=name,
                        old_hash=old_entry["entry"][hash_col],
                        old_path=old_entry["path"],
                    )
                )
            else:
                new_entry = new_index[name]
                if old_entry["entry"][hash_col] != new_entry["entry"][hash_col]:
                    changes.append(
                        FileChange(
                            change_type=ChangeType.MODIFIED,
                            path=name,
                            old_hash=old_entry["entry"][hash_col],
                            new_hash=new_entry["entry"][hash_col],
                            old_path=old_entry["path"],
                            new_path=new_entry["path"],
                        )
                    )

        # Check for added and moved files
        for name, new_entry in new_index.items():
            if name not in old_index:
                moved = False
                for _old_name, old_entry in old_index.items():
                    if old_entry["entry"][hash_col] == new_entry["entry"][hash_col]:
                        changes.append(
                            FileChange(
                                change_type=ChangeType.MOVED,
                                path=name,
                                old_path=old_entry["path"],
                                new_path=new_entry["path"],
                                old_hash=old_entry["entry"][hash_col],
                                new_hash=new_entry["entry"][hash_col],
                            )
                        )
                        moved = True
                        break

                if not moved:
                    changes.append(
                        FileChange(
                            change_type=ChangeType.ADDED,
                            path=name,
                            new_hash=new_entry["entry"][hash_col],
                            new_path=new_entry["path"],
                        )
                    )

        # Sort changes by type then path
        return sorted(changes, key=lambda x: (x.change_type.value, x.path.lower()))

    def get_output_filename(self, report1: str, report2: str, output_dir: str) -> Path:
        """Generate comparison output filename."""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        # Extract report names
        old_name = Path(report1).stem
        new_name = Path(report2).stem
        # Remove common prefix from second report
        parts = new_name.split("_")
        if len(parts) > 1:
            new_name = "_".join(parts[1:])

        return output_path / f"compare_{old_name}_{new_name}.csv"

    def format_changes_for_save(self, changes: List[FileChange]) -> List[Dict]:
        """Format changes into saveable data structure."""
        return [
            {
                "Change Type": str(change.change_type),
                "Path": change.path,
                "Old Hash": change.old_hash or "",
                "New Hash": change.new_hash or "",
                "Old Path": change.old_path or "",
                "New Path": change.new_path or "",
            }
            for change in changes
        ]
