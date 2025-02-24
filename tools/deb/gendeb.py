#!/usr/bin/env python3
"""Generate Debian package control files from project metadata."""

import sys
import textwrap
from datetime import datetime
from pathlib import Path
from typing import Any, List, Tuple

sys.path.append(str(Path(__file__).parent.parent))

from hashreport.config import get_config  # noqa: E402

CONTROL_TEMPLATE = """\
Source: python3-{name}
Section: utils
Priority: optional
Maintainer: {maintainer}
Build-Depends: debhelper-compat (= 13),
               dh-python,
               python3-all,
               python3-poetry,
               python3-setuptools,
               {build_depends}
Standards-Version: 4.6.0
Homepage: {homepage}
Rules-Requires-Root: no

Package: python3-{name}
Architecture: all
Depends: python3,
         {depends}
Description: {description}
{long_description}
"""

RULES_TEMPLATE = """\
#!/usr/bin/make -f
%:
    dh $@ --with python3 --buildsystem=pybuild

override_dh_auto_build:
    poetry build

override_dh_auto_install:
    poetry install --no-dev --root debian/python3-{name}
"""

COPYRIGHT_TEMPLATE = """\
Format: https://www.debian.org/doc/packaging-manuals/copyright-format/1.0/
Upstream-Name: {name}
Source: {homepage}

Files: *
Copyright: {year} {author}
License: {license}
"""

COMPAT_CONTENT = "13\n"


def format_dependencies(deps: List[str]) -> str:
    """Format dependencies for control file."""
    return ",\n         ".join(f"python3-{dep}" for dep in deps)


def format_build_dependencies(deps: List[str]) -> str:
    """Format build dependencies for control file."""
    return ",\n               ".join(f"python3-{dep}" for dep in deps)


def wrap_description(desc: str) -> str:
    """Wrap long description text according to Debian control file format."""
    lines = []
    for line in desc.split("\n"):
        if line.strip():
            lines.extend(" " + line_part for line_part in textwrap.wrap(line, width=76))
        else:
            lines.append(" .")
    return "\n".join(lines)


def parse_changelog(changelog_path: Path, version: str) -> Tuple[str, str, str]:
    """Parse the CHANGELOG.md file for the specified version."""
    if not changelog_path.exists():
        return "", "", ""

    current_version = ""
    current_date = ""
    changes = []
    in_target_version = False

    for line in changelog_path.read_text().splitlines():
        if line.startswith("## v"):
            if in_target_version:
                break
            parts = line.split()
            current_version = parts[1].lstrip("v")
            if current_version == version:
                in_target_version = True
                current_date = parts[2].strip("()")
        elif in_target_version and line.strip() and not line.startswith("#"):
            # Strip Markdown formatting and normalize entry
            entry = line.strip()
            if entry.startswith("- "):
                entry = entry[2:]
            entry = entry.replace("**", "").replace("`: ", ": ")
            if entry:
                changes.append("  * " + entry)

    return current_version, current_date, "\n".join(changes)


def generate_changelog(
    package: str,
    version: str,
    changes: str,
    date: str,
    maintainer: str,
    distribution: str = "unstable",
    urgency: str = "medium",
) -> str:
    """Generate Debian changelog entry."""
    date_obj = datetime.strptime(date, "%Y-%m-%d")
    deb_date = date_obj.strftime("%a, %d %b %Y %H:%M:%S +0000")

    return f"""{package} ({version}-1) {distribution}; urgency={urgency}

{changes}

 -- {maintainer}  {deb_date}
"""


def get_dependencies(config: Any) -> Tuple[List[str], List[str]]:
    """Extract runtime and build dependencies from poetry config."""
    # Get dependencies from pyproject.toml
    runtime_deps = set()
    build_deps = set()

    # Add core dependencies
    runtime_deps.add("python3")
    build_deps.update(
        ["setuptools", "poetry", "all"]
    )  # Remove python3- prefix, handled by formatter

    # Add project dependencies
    poetry_config = config._load_toml(config.PROJECT_CONFIG_PATH)
    if "tool" in poetry_config and "poetry" in poetry_config["tool"]:
        deps = poetry_config["tool"]["poetry"].get("dependencies", {})
        dev_deps = poetry_config["tool"]["poetry"].get("dev-dependencies", {})

        # Strip python3- prefix if present
        runtime_deps.update(
            dep.split("[")[0].lower().replace("python3-", "")
            for dep in deps
            if dep != "python"
        )
        build_deps.update(
            dep.split("[")[0].lower().replace("python3-", "") for dep in dev_deps
        )

    return sorted(runtime_deps), sorted(build_deps)


def format_description(desc: str) -> str:
    """Format package description according to Debian standards."""
    lines = desc.split("\n")
    short_desc = lines[0].strip()

    # Format long description with proper indentation and line wrapping
    long_desc = []
    for line in lines[1:]:
        if not line.strip():
            long_desc.append(" .")
        else:
            # Wrap at 72 chars and indent with 2 spaces
            wrapped = textwrap.fill(
                line.strip(), width=70, initial_indent=" ", subsequent_indent=" "
            )
            long_desc.append(wrapped)

    return short_desc, "\n".join(long_desc)


def main() -> None:
    """Generate Debian package files."""
    config = get_config()
    metadata = config.get_metadata()
    maintainer = metadata["authors"][0]
    homepage = metadata["urls"].get("Repository", "")
    package_name = metadata["name"]  # Original package name without python3- prefix

    # Get dependencies
    runtime_deps, build_deps = get_dependencies(config)

    # Format description
    short_desc, long_desc = format_description(metadata["description"])

    # Create debian directory
    debian_dir = Path("debian")
    debian_dir.mkdir(exist_ok=True)

    # Parse changelog for current version
    changelog_path = Path("CHANGELOG.md")
    version, date, changes = parse_changelog(changelog_path, metadata["version"])
    if not all([version, date, changes]):
        # Fallback if changelog entry not found
        version = metadata["version"]
        date = datetime.now().strftime("%Y-%m-%d")
        changes = "* Initial release."

    # Generate and write control file
    control_content = CONTROL_TEMPLATE.format(
        name=package_name,  # This will create python3-hashreport consistently
        maintainer=maintainer,
        homepage=homepage,
        build_depends=format_build_dependencies(build_deps),
        depends=format_dependencies(runtime_deps),
        description=short_desc,
        long_description=long_desc,
    )
    (debian_dir / "control").write_text(control_content)

    # Generate and write changelog
    changelog_content = generate_changelog(
        f"python3-{package_name}",
        version,
        changes,
        date,
        maintainer,
    )
    (debian_dir / "changelog").write_text(changelog_content)

    # Generate and write rules file
    rules_content = RULES_TEMPLATE.format(name=metadata["name"])
    rules_file = debian_dir / "rules"
    rules_file.write_text(rules_content)
    rules_file.chmod(0o755)

    # Generate and write copyright file
    copyright_content = COPYRIGHT_TEMPLATE.format(
        name=metadata["name"],
        homepage=homepage,
        year=datetime.now().year,
        author=maintainer.split("<")[0].strip(),
        license=metadata["license"],
    )
    (debian_dir / "copyright").write_text(copyright_content)

    # Write compat file
    (debian_dir / "compat").write_text(COMPAT_CONTENT)

    print(f"Generated Debian package files in {debian_dir}")


if __name__ == "__main__":
    main()
