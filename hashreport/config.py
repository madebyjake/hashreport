"""Configuration management for hashreport."""

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, ClassVar, Dict, List, Optional

import tomli

from hashreport.utils.type_defs import (
    ConfigDict,
    EmailConfig,
    validate_hash_algorithm,
    validate_report_format,
)

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
    DEFAULT_EMAIL_CONFIG: ClassVar[EmailConfig] = {
        "port": 587,
        "use_tls": True,
        "host": "localhost",
    }

    # Application settings with type-safe defaults
    default_algorithm: str = "md5"
    default_format: str = "csv"
    supported_formats: List[str] = field(default_factory=lambda: ["csv", "json"])
    chunk_size: int = 4096
    mmap_threshold: int = 10485760  # 10MB default threshold for mmap usage
    timestamp_format: str = "%y%m%d-%H%M"
    show_progress: bool = True
    max_errors_shown: int = 10
    email_defaults: EmailConfig = field(default_factory=dict)

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
    memory_threshold: float = 0.85

    # Progress display settings
    progress: Dict[str, Any] = field(
        default_factory=lambda: {
            "refresh_rate": 0.1,
            "show_eta": True,
            "show_file_names": False,
            "show_speed": True,
        }
    )

    def __post_init__(self) -> None:
        """Validate configuration after initialization."""
        self._initialize_defaults()
        self._validate_configuration()

    def _initialize_defaults(self) -> None:
        """Initialize default values based on system resources."""
        # Set memory limit if not specified
        if self.memory_limit is None:
            try:
                import psutil

                total_memory = psutil.virtual_memory().total
                # 75% of total RAM
                self.memory_limit = int(total_memory * 0.75 / (1024 * 1024))
            except ImportError:
                self.memory_limit = 1024  # Default to 1GB

        # Set max_workers if not specified
        if self.max_workers is None:
            try:
                import os

                self.max_workers = min(32, (os.cpu_count() or 4) * 2)
            except Exception:
                self.max_workers = 8

    def _validate_configuration(self) -> None:
        """Validate configuration settings."""
        errors = []

        # Validate hash algorithm
        try:
            validate_hash_algorithm(self.default_algorithm)
        except ValueError as e:
            errors.append(str(e))

        # Validate report format
        try:
            validate_report_format(self.default_format)
        except ValueError as e:
            errors.append(str(e))

        # Validate supported formats
        for fmt in self.supported_formats:
            try:
                validate_report_format(fmt)
            except ValueError as e:
                errors.append(f"Unsupported format '{fmt}': {e}")

        # Validate numeric ranges
        if self.chunk_size <= 0:
            errors.append("chunk_size must be positive")
        if self.mmap_threshold <= 0:
            errors.append("mmap_threshold must be positive")
        if self.batch_size <= 0:
            errors.append("batch_size must be positive")
        if self.max_retries < 0:
            errors.append("max_retries must be non-negative")
        if self.retry_delay < 0:
            errors.append("retry_delay must be non-negative")
        if self.min_workers <= 0:
            errors.append("min_workers must be positive")
        if self.max_workers is not None and self.max_workers <= 0:
            errors.append("max_workers must be positive")
        if self.max_workers is not None and self.min_workers > self.max_workers:
            errors.append("min_workers cannot exceed max_workers")
        if self.memory_threshold <= 0 or self.memory_threshold > 1:
            errors.append("memory_threshold must be between 0 and 1")

        # Validate email configuration
        if self.email_defaults:
            port = self.email_defaults.get("port")
            if port is not None and (
                not isinstance(port, int) or port <= 0 or port > 65535
            ):
                errors.append("email port must be a valid port number (1-65535)")

        if errors:
            raise ValueError(f"Configuration validation failed: {'; '.join(errors)}")

    @classmethod
    def _find_valid_config(cls, path: Path) -> Optional[ConfigDict]:
        """Search for a valid config file in this path or its parents."""
        current = path if path.is_absolute() else Path.cwd() / path
        while current != current.parent:
            config_path = current / cls.PROJECT_CONFIG_PATH
            if config_path.exists():
                try:
                    with config_path.open("rb") as f:
                        data = tomli.load(f)
                        return data
                except Exception as e:
                    logger.debug(
                        "Skipping invalid config at %s: %s", config_path, str(e)
                    )
            current = current.parent
        return None

    @classmethod
    def from_file(cls, config_path: Optional[Path] = None) -> "HashReportConfig":
        """Load configuration from a TOML file.

        Args:
            config_path: Optional path to config file, defaults to pyproject.toml

        Returns:
            HashReportConfig instance with loaded settings

        Raises:
            ValueError: If configuration validation fails
        """
        path = config_path or cls.PROJECT_CONFIG_PATH

        # Find valid config data
        data = cls._find_valid_config(path)
        if not data:
            return cls()

        tool_section = data.get("tool", {})
        app_config = tool_section.get(cls.APP_CONFIG_KEY, {})

        try:
            return cls(**app_config)
        except Exception as e:
            logger.warning(f"Failed to load config from {path}, using defaults: {e}")
            return cls()

    @classmethod
    def _load_toml(cls, config_path: Path) -> ConfigDict:
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
    def load_settings(cls) -> ConfigDict:
        """Load user settings from settings file.

        Returns:
            Dictionary containing user settings or empty dict if file doesn't exist
        """
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

    def get_user_settings(self) -> ConfigDict:
        """Get user-editable settings as a dictionary."""
        return self.load_settings()

    def get_all_settings(self) -> ConfigDict:
        """Get complete configuration settings."""
        settings = self.get_user_settings()
        for section in ["email_defaults", "logging", "progress", "reports"]:
            if section not in settings:
                if section == "email_defaults":
                    # Use default email config if email_defaults is empty
                    settings[section] = self.email_defaults or self.DEFAULT_EMAIL_CONFIG
                else:
                    settings[section] = getattr(self, section, {})
        return settings

    def to_dict(self) -> ConfigDict:
        """Convert configuration to dictionary representation.

        Returns:
            Dictionary containing all configuration values
        """
        return {
            "default_algorithm": self.default_algorithm,
            "default_format": self.default_format,
            "supported_formats": self.supported_formats,
            "chunk_size": self.chunk_size,
            "mmap_threshold": self.mmap_threshold,
            "timestamp_format": self.timestamp_format,
            "show_progress": self.show_progress,
            "max_errors_shown": self.max_errors_shown,
            "email_defaults": self.email_defaults,
            "batch_size": self.batch_size,
            "max_retries": self.max_retries,
            "retry_delay": self.retry_delay,
            "memory_limit": self.memory_limit,
            "min_workers": self.min_workers,
            "max_workers": self.max_workers,
            "worker_adjust_interval": self.worker_adjust_interval,
            "progress_update_interval": self.progress_update_interval,
            "resource_check_interval": self.resource_check_interval,
            "memory_threshold": self.memory_threshold,
            "progress": self.progress,
        }


# Global configuration instance
_config_instance: Optional[HashReportConfig] = None


def get_config() -> HashReportConfig:
    """Get the global configuration instance.

    Returns:
        HashReportConfig instance
    """
    global _config_instance
    if _config_instance is None:
        _config_instance = HashReportConfig.from_file()
    return _config_instance


def reset_config() -> None:
    """Reset the global configuration instance."""
    global _config_instance
    _config_instance = None
