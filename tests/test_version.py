"""Tests for the version module."""

import importlib
from unittest.mock import patch


def test_version_when_package_found():
    """Test version when package is found in metadata."""
    with patch("importlib.metadata.version", return_value="1.2.3"):
        # Force reload to pickup mocked version
        import hashreport.version

        importlib.reload(hashreport.version)
        assert hashreport.version.__version__ == "1.2.3"


def test_version_when_package_not_found():
    """Test version when package is not found in metadata."""
    with patch(
        "importlib.metadata.version",
        side_effect=importlib.metadata.PackageNotFoundError,
    ):
        import hashreport.version

        importlib.reload(hashreport.version)
        assert hashreport.version.__version__ == "0.0.0"
