"""Version information for the hashreport package."""

import importlib.metadata

try:
    __version__ = importlib.metadata.version("hashreport")
except importlib.metadata.PackageNotFoundError:
    __version__ = "0.0.0"  # Fallback version
