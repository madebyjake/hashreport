"""Configuration and constants module for the hashreport package."""

import pathlib
from typing import Any, Dict

import tomli


class ConfigLoader:
    """
    Load the pyproject.toml configuration file.

    Args:
        config_path (pathlib.Path): The path to the configuration file

    Attributes:
        config_path (pathlib.Path): The path to the configuration file
        config (Dict[str, Any]): The configuration file as a dictionary

    Raises:
        FileNotFoundError: If the configuration file is not found
        ValueError: If there is an error decoding the TOML file
    """

    def __init__(self, config_path: pathlib.Path):
        """Initialize the ConfigLoader.

        Args:
            config_path (pathlib.Path): Path to the configuration file
        """
        self.config_path = config_path
        self.config = self.load_config()

    def load_config(self) -> Dict[str, Any]:
        """Load and parse the TOML configuration file.

        Returns:
            Dict[str, Any]: The parsed configuration data

        Raises:
            FileNotFoundError: If the configuration file is not found
            ValueError: If there is an error decoding the TOML file
        """
        if not self.config_path.exists():
            raise FileNotFoundError(f"Config file not found: {self.config_path}")

        try:
            with self.config_path.open("r", encoding="utf-8") as f:
                return tomli.loads(f.read())
        except (tomli.TOMLDecodeError, UnicodeDecodeError) as e:
            raise ValueError(f"Error decoding TOML file: {e}")


try:
    config_loader = ConfigLoader(
        pathlib.Path(__file__).parent.parent / "pyproject.toml"
    )
    pyproject_data = config_loader.config
except FileNotFoundError:
    pyproject_data = {}

TOOL_POETRY = pyproject_data.get("tool", {}).get("poetry", {})


class GlobalConstants:
    """
    Global constants for the project.

    Args:
        tool_poetry (Dict[str, Any]): The poetry section of the pyproject.toml file

    Attributes:
        authors (str): The authors of the project
        description (str): The description of the project
        license (str): The license of the project
        name (str): The name of the project
        urls (Dict[str, str]): The URLs of the project
        version (str): The version of the project
    """

    def __init__(self, tool_poetry: Dict[str, Any]):
        """Initialize GlobalConstants with poetry configuration.

        Args:
            tool_poetry (Dict[str, Any]): The poetry section of pyproject.toml
        """
        self._authors = tool_poetry.get("authors", [])
        self._description = tool_poetry.get("description", "")
        self._license = tool_poetry.get("license", "")
        self._name = tool_poetry.get("name", "")
        self._urls = tool_poetry.get("urls", {})
        self._version = tool_poetry.get("version", "")

    @property
    def AUTHORS(self):
        """Get the project authors.

        Returns:
            list: List of project authors
        """
        return self._authors

    @property
    def DESCRIPTION(self):
        """Get the project description.

        Returns:
            str: Project description
        """
        return self._description

    @property
    def LICENSE(self):
        """Get the project license.

        Returns:
            str: Project license
        """
        return self._license

    @property
    def NAME(self):
        """Get the project name.

        Returns:
            str: Project name
        """
        return self._name

    @property
    def URLS(self):
        """Get the project URLs.

        Returns:
            Dict[str, str]: Dictionary of project URLs
        """
        return self._urls

    @property
    def VERSION(self):
        """Get the project version.

        Returns:
            str: Project version
        """
        return self._version


global_const = GlobalConstants(TOOL_POETRY)
