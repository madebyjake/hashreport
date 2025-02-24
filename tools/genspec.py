#!/usr/bin/env python3
"""Generate RPM spec file from project metadata."""

import sys
from datetime import datetime
from pathlib import Path
from typing import List, Tuple

sys.path.append(str(Path(__file__).parent.parent))

from hashreport.config import get_config  # noqa: E402

SPEC_TEMPLATE = """\
Name:           {name}
Version:        {version}
Release:        1%{{?dist}}
Summary:        {summary}

License:        {license}
URL:            {url}
Source0:        %{{name}}-%{{version}}.tar.gz

BuildArch:      noarch
BuildRequires:  python3-devel
BuildRequires:  python3-pip
BuildRequires:  python3-poetry
BuildRequires:  python3-setuptools
{build_requires}

Requires:       python3
{requires}

%description
{description}

%prep
%autosetup

%build
poetry build

%install
rm -rf $RPM_BUILD_ROOT
poetry install --no-dev --root $RPM_BUILD_ROOT

%files
%license LICENSE
%doc README.md
%{{_bindir}}/hashreport
%{{python3_sitelib}}/hashreport/
%{{python3_sitelib}}/hashreport-*.dist-info/

%changelog
"""


def format_dependencies(deps: List[str]) -> str:
    """Format dependencies for spec file."""
    return "\n".join(f"Requires:       python3-{dep}" for dep in deps)


def format_build_requires(deps: List[str]) -> str:
    """Format build requirements for spec file."""
    return "\n".join(f"BuildRequires:  python3-{dep}" for dep in deps)


def parse_changelog(changelog_path: Path) -> List[Tuple[str, str, str]]:
    """Parse the CHANGELOG.md file and return a list of (version, date, changes)."""
    if not changelog_path.exists():
        return []

    entries = []
    current_version = current_date = current_changes = ""

    for line in changelog_path.read_text().splitlines():
        if line.startswith("## v"):
            if current_version:
                entries.append((current_version, current_date, current_changes.strip()))
            current_changes = ""
            parts = line.split()
            current_version = parts[1].lstrip("v")
            # Parse date from format (YYYY-MM-DD)
            current_date = parts[2].strip("()")
        elif line.strip() and not line.startswith("#"):
            current_changes += f"{line}\n"

    if current_version:
        entries.append((current_version, current_date, current_changes.strip()))

    return entries


def format_changelog_entries(
    entries: List[Tuple[str, str, str]], packager: str, version: str
) -> str:
    """Format changelog entries for the spec file."""
    changelog = []
    for entry_version, date, changes in entries:
        if entry_version == version:
            date_obj = datetime.strptime(date, "%Y-%m-%d")
            rpm_date = date_obj.strftime("%a %b %d %Y")
            changelog.append(f"* {rpm_date} {packager} - {version}-1")
            for line in changes.split("\n"):
                if line.strip():
                    changelog.append(f"- {line.strip()}")
            break  # Only include the matching version
    return "\n".join(changelog)


def main() -> None:
    """Generate spec file from project metadata."""
    config = get_config()
    metadata = config.get_metadata()

    # Extract dependencies from pyproject.toml
    deps = ["click", "rich", "tomli", "tqdm", "typing-extensions"]
    build_deps = ["pytest", "black", "flake8", "isort"]

    # Parse changelog
    changelog_path = Path(__file__).parent.parent / "CHANGELOG.md"
    changelog_entries = parse_changelog(changelog_path)

    # Get the latest date for the current version
    current_version_entry = next(
        (entry for entry in changelog_entries if entry[0] == metadata["version"]), None
    )
    if current_version_entry:
        date_str = datetime.strptime(current_version_entry[1], "%Y-%m-%d").strftime(
            "%a %b %d %Y"
        )
    else:
        date_str = datetime.now().strftime("%a %b %d %Y")

    # Generate changelog content
    changelog_content = format_changelog_entries(
        changelog_entries,
        metadata["authors"][0].split("<")[0].strip(),
        metadata["version"],
    )

    # Format the spec file
    spec_content = SPEC_TEMPLATE.format(
        name=metadata["name"],
        version=metadata["version"],
        summary=metadata["description"].split("\n")[0],
        description=metadata["description"],
        license=metadata["license"],
        url=metadata["urls"].get("Repository", ""),
        requires=format_dependencies(deps),
        build_requires=format_build_requires(build_deps),
        date=date_str,
        packager=metadata["authors"][0].split("<")[0].strip(),
    )

    # Append changelog
    spec_content = spec_content.rstrip() + "\n" + changelog_content

    # Write to file
    spec_file = Path(f"{metadata['name']}.spec")
    spec_file.write_text(spec_content)
    print(f"Generated spec file: {spec_file}")


if __name__ == "__main__":
    main()
