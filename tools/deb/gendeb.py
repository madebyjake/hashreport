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
Source: {name}
Section: utils
Priority: optional
Maintainer: {maintainer}
Build-Depends: debhelper-compat (= 13),
               dh-python,
               python3-all,
               python3-setuptools,
               pybuild-plugin-pyproject,
               {build_depends}
Standards-Version: 4.6.0
Homepage: {homepage}
Rules-Requires-Root: no

Package: {name}
Architecture: all
Depends: python3,
         python3-pkg-resources,
         ${{python3:Depends}},
         {depends}
Description: {description}
{long_description}
"""

RULES_TEMPLATE = """\
#!/usr/bin/make -f

export DESTDIR=$(CURDIR)/debian/python3-{name}
export PYBUILD_NAME=hashreport
export PYBUILD_SYSTEM=distutils
export PYBUILD_DISABLE=test

%:
\tdh $@ --with python3 --buildsystem=pybuild

override_dh_auto_build:
\tdh_auto_build
\tpython3 tools/docs/genman.py

override_dh_auto_install:
\tdh_auto_install
\tdh_python3
\tmkdir -p $(DESTDIR)/usr/share/man/man1
\tcp -p man/man1/hashreport.1 $(DESTDIR)/usr/share/man/man1/
"""

COPYRIGHT_TEMPLATE = """\
Format: https://www.debian.org/doc/packaging-manuals/copyright-format/1.0/
Upstream-Name: {name}
Source: {homepage}

Files: *
Copyright: {year} {author}
License: {license}
"""


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
    runtime_deps = []
    build_deps = []

    # Add project dependencies
    poetry_config = config._load_toml(config.PROJECT_CONFIG_PATH)
    if "tool" in poetry_config and "poetry" in poetry_config["tool"]:
        poetry_section = poetry_config["tool"]["poetry"]

        # Handle runtime dependencies
        if "dependencies" in poetry_section:
            deps = poetry_section["dependencies"]
            if isinstance(deps, dict):  # Handle dict format
                runtime_deps.extend(
                    name.split("[")[0].lower()
                    for name in deps.keys()
                    if name != "python"
                )

        # Handle build dependencies
        for group in ["dev-dependencies", "group.dev.dependencies"]:
            if group in poetry_section:
                dev_deps = poetry_section[group]
                if isinstance(dev_deps, dict):
                    build_deps.extend(
                        name.split("[")[0].lower() for name in dev_deps.keys()
                    )

    return sorted(runtime_deps), sorted(build_deps)


def format_description(desc: str) -> tuple[str, str]:
    """Format package description according to Debian standards."""
    lines = desc.split("\n")
    # Take first sentence for summary, limit to 60 chars
    summary = lines[0].split(".")[0].strip()[:60]

    # Format long description with proper indentation
    long_desc = []
    for line in lines[1:]:
        if not line.strip():
            long_desc.append(" .")
        else:
            # Wrap and indent continuation lines
            wrapped = textwrap.fill(
                line.strip(), width=70, initial_indent=" ", subsequent_indent="  "
            )
            long_desc.append(wrapped)

    return summary, "\n".join(long_desc)


def main() -> None:
    """Generate Debian package files."""
    config = get_config()
    metadata = config.get_metadata()
    maintainer = metadata["authors"][0]
    homepage = metadata["urls"].get("Repository", "")
    package_name = f"python3-{metadata['name']}"  # Add python3- prefix here

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
        version = metadata["version"]
        date = datetime.now().strftime("%Y-%m-%d")
        changes = "* Initial release."

    # Write package files
    control_content = CONTROL_TEMPLATE.format(
        name=package_name,
        maintainer=maintainer,
        homepage=homepage,
        build_depends=format_build_dependencies(build_deps),
        depends=format_dependencies(runtime_deps),
        description=short_desc,
        long_description=long_desc,
    )
    (debian_dir / "control").write_text(control_content)

    # Write changelog with the python3- prefix in package name
    changelog_content = generate_changelog(
        package_name,
        version,
        changes,
        date,
        maintainer,
    )
    (debian_dir / "changelog").write_text(changelog_content)

    # Write rules file with the original package name (without python3- prefix)
    rules_content = RULES_TEMPLATE.format(name=metadata["name"])
    rules_file = debian_dir / "rules"
    rules_file.write_text(rules_content)
    rules_file.chmod(0o755)

    # Write copyright file
    copyright_content = COPYRIGHT_TEMPLATE.format(
        name=metadata["name"],
        homepage=homepage,
        year=datetime.now().year,
        author=maintainer.split("<")[0].strip(),
        license=metadata["license"],
    )
    (debian_dir / "copyright").write_text(copyright_content)

    print(f"Generated Debian package files in {debian_dir}")


if __name__ == "__main__":
    main()
