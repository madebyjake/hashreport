"""Configuration management for hashreport."""

import logging
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, ClassVar, Dict, List, Optional, Union

import tomli

from hashreport.utils.exceptions import ConfigError

logger = logging.getLogger(__name__)


@dataclass
class HashReportConfig:
    """Configuration settings for hashreport."""

    # Class-level constants
    PROJECT_CONFIG_PATH: ClassVar[Path] = Path("pyproject.toml")
    SETTINGS_PATH: ClassVar[Path] = (
        Path.home() / ".config" / "hashreport" / "settings.toml"
    )
    APP_CONFIG_KEY: ClassVar[str] = "hashreport"
    POETRY_CONFIG_KEY: ClassVar[str] = "poetry"
    DEFAULT_EMAIL_CONFIG: ClassVar[Dict[str, Union[int, bool, str]]] = {
        "port": 587,
        "use_tls": True,
        "host": "localhost",
    }
    REQUIRED_METADATA: ClassVar[List[str]] = ["name", "version"]

    # Application settings with type-safe defaults
    default_algorithm: str = "md5"
    default_format: str = "csv"
    supported_formats: List[str] = field(default_factory=lambda: ["csv", "json"])
    chunk_size: int = 4096
    mmap_threshold: int = 10485760  # 10MB default threshold for mmap usage
    max_workers: Optional[int] = None
    timestamp_format: str = "%y%m%d-%H%M"
    show_progress: bool = True
    max_errors_shown: int = 10
    email_defaults: Dict[str, Any] = field(default_factory=dict)

    # Settings for resource management
    batch_size: int = 1000
    max_retries: int = 3
    retry_delay: float = 1.0
    memory_limit: Optional[int] = None  # in MB
    min_workers: int = 2
    max_workers: Optional[int] = None
    worker_adjust_interval: int = 60  # seconds
    progress_update_interval: float = 0.1  # seconds
    resource_check_interval: float = 1.0  # seconds
    memory_threshold: float = 0.85  # 85% memory usage threshold

    # Project metadata - loaded dynamically from pyproject.toml
    name: str = field(init=False)
    version: str = field(init=False)
    description: str = field(init=False, default="")
    authors: List[str] = field(init=False, default_factory=list)
    project_license: str = field(init=False, default="")
    urls: Dict[str, str] = field(init=False, default_factory=dict)

    def __post_init__(self) -> None:
        """Initialize computed values."""
        if not self.email_defaults:
            self.email_defaults = self.DEFAULT_EMAIL_CONFIG.copy()
        if self.max_workers is None:
            self.max_workers = os.cpu_count() or 4

        if not self.memory_limit:
            import psutil

            total_memory = psutil.virtual_memory().total
            self.memory_limit = int(
                total_memory * 0.75 / (1024 * 1024)
            )  # 75% of total RAM

        if self.max_workers is None:
            self.max_workers = os.cpu_count() or 4

        # Ensure min_workers doesn't exceed max_workers
        self.min_workers = min(self.min_workers, self.max_workers)

    @classmethod
    def _validate_metadata(cls, data: Dict[str, Any]) -> None:
        """Validate required metadata fields exist.

        Args:
            data: Poetry metadata section

        Raises:
            ConfigError: If required fields are missing or invalid
        """
        missing = [field for field in cls.REQUIRED_METADATA if field not in data]
        if missing:
            raise ConfigError(
                f"Missing required metadata fields in pyproject.toml: {', '.join(missing)}"  # noqa: E501
            )

        # Validate version format
        if not isinstance(data["version"], str) or not data["version"].strip():
            raise ConfigError("Version must be a non-empty string in pyproject.toml")

    @classmethod
    def _load_metadata(cls, poetry_config: Dict[str, Any]) -> Dict[str, Any]:
        """Extract and validate metadata from poetry configuration.

        Args:
            poetry_config: Poetry section from pyproject.toml

        Returns:
            Dictionary of validated metadata

        Raises:
            ValueError: If required metadata is missing
        """
        cls._validate_metadata(poetry_config)
        return {
            "name": poetry_config["name"],
            "version": poetry_config["version"],
            "description": poetry_config.get("description", ""),
            "authors": poetry_config.get("authors", []),
            "project_license": poetry_config.get("license", ""),
            "urls": poetry_config.get("urls", {}),
        }

    @classmethod
    def _find_valid_config(cls, path: Path) -> Optional[Dict[str, Any]]:
        """Search for a valid config file in this path or its parents.

        Args:
            path: Starting path for search

        Returns:
            Dict containing valid config data or None if no valid config found
        """
        current = path if path.is_absolute() else Path.cwd() / path
        while current != current.parent:
            config_path = current / cls.PROJECT_CONFIG_PATH
            if config_path.exists():
                try:
                    with config_path.open("rb") as f:
                        data = tomli.load(f)
                        # Check if this is a valid poetry config
                        poetry_data = data.get("tool", {}).get(
                            cls.POETRY_CONFIG_KEY, {}
                        )
                        if all(field in poetry_data for field in cls.REQUIRED_METADATA):
                            return data
                except Exception as e:
                    logger.debug(
                        "Skipping invalid config at %s: %s", config_path, str(e)
                    )
                    # Continue searching parent directories
            current = current.parent
        return None

    @classmethod
    def from_file(cls, config_path: Optional[Path] = None) -> "HashReportConfig":
        """Load configuration from a TOML file."""
        path = config_path or cls.PROJECT_CONFIG_PATH

        # Find valid config data
        data = cls._find_valid_config(path)
        if not data:
            raise ConfigError(
                "No valid configuration found. Ensure pyproject.toml exists with required metadata."  # noqa: E501
            )

        tool_section = data.get("tool", {})
        app_config = tool_section.get(cls.APP_CONFIG_KEY, {})
        poetry_config = tool_section.get(cls.POETRY_CONFIG_KEY, {})

        if not poetry_config:
            raise ConfigError("Missing [tool.poetry] section in pyproject.toml")

        try:
            metadata = cls._load_metadata(poetry_config)
            instance = cls(**app_config)
            for key, value in metadata.items():
                setattr(instance, key, value)
            return instance
        except (ValueError, ConfigError) as e:
            logger.error("Configuration error: %s", e)
            raise ConfigError(str(e))

    @classmethod
    def _load_toml(cls, config_path: Path) -> Dict[str, Any]:
        """Load and parse TOML file with proper error handling.

        Args:
            config_path: Path to the TOML file

        Returns:
            Dictionary containing parsed TOML data or empty dict on error
        """
        if not config_path.exists():
            logger.warning("Config file not found: %s", config_path)
            return {}

        try:
            with config_path.open("rb") as f:
                return tomli.load(f)
        except tomli.TOMLDecodeError as e:
            logger.error("Error decoding TOML file: %s", e)
            return {}
        except Exception as e:
            logger.error("Unexpected error reading config: %s", e)
            return {}

    @classmethod
    def get_settings_path(cls) -> Path:
        """Get the user's settings file path."""
        return cls.SETTINGS_PATH

    @classmethod
    def load_settings(cls) -> Dict[str, Any]:
        """Load user settings from settings file."""
        settings_path = cls.get_settings_path()
        if not settings_path.exists():
            return {}
        try:
            with settings_path.open("rb") as f:
                data = tomli.load(f)
                return data.get(cls.APP_CONFIG_KEY, {})
        except Exception as e:
            logger.warning(f"Error loading settings: {e}")
            return {}

    def get_user_settings(self) -> Dict[str, Any]:
        """Get user-editable settings as a dictionary."""
        return self.load_settings()

    def get_metadata(self) -> Dict[str, Any]:
        """Get project metadata as a dictionary."""
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "authors": self.authors,
            "license": self.project_license,
            "urls": self.urls,
        }

    def get_all_settings(self) -> Dict[str, Any]:
        """Get complete configuration settings."""
        settings = self.get_user_settings()
        for section in ["email_defaults", "logging", "progress", "reports"]:
            if section not in settings:
                settings[section] = getattr(self, section, {})
        return settings


# Lazy-loaded configuration instance
loaded_config = None


def get_config() -> HashReportConfig:
    """Get the loaded configuration instance."""
    global loaded_config
    if loaded_config is None:
        try:
            loaded_config = HashReportConfig.from_file()
        except Exception as e:
            logger.error(f"Error loading config, falling back to defaults: {e}")
            loaded_config = HashReportConfig()
            loaded_config.name = "hashreport"
            loaded_config.version = "0.0.0"
    return loaded_config
