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
Summary:        Generate detailed file hash reports

License:        AGPLv3
URL:            {url}
Source0:        %{{name}}-%{{version}}.tar.gz

BuildArch:      noarch
BuildRequires:  python3-devel
BuildRequires:  python3-pip
BuildRequires:  python3-setuptools
BuildRequires:  python3-wheel
{build_requires}

Requires:       python3
{requires}

%description
A command-line tool that generates comprehensive hash reports for files within
a directory. Reports can be output in CSV or JSON formats and include detailed
information such as file name, path, size, hash algorithm, hash value, and
last modified date.

Features:
* Support for multiple hash algorithms
* Multi-threaded processing
* Configurable output formats
* File filtering options
* Email report delivery

%prep
%autosetup

%build
# Install build dependencies first
python3 -m pip install --upgrade pip wheel
python3 -m pip install rich click tomli tqdm typing-extensions psutil

# Build wheel without dependencies (they're handled by RPM)
python3 -m pip wheel --no-deps -w dist .

# Generate man pages with required dependencies available
PYTHONPATH=. python3 tools/gen_man.py

# Don't run tests during package build
%define _skip_tests 1

%install
rm -rf %{{buildroot}}
# Install just our package wheel, dependencies are handled by RPM
python3 -m pip install --root=%{{buildroot}} --no-deps dist/*.whl

# Fix permissions and move binaries to standard location
mkdir -p %{{buildroot}}%{{_bindir}}
for bindir in %{{buildroot}}/usr/bin %{{buildroot}}/usr/local/bin; do
    if [ -d "$bindir" ]; then
        find "$bindir" -type f -exec mv '{{}}' %{{buildroot}}%{{_bindir}}/ \\;
    fi
done

# Install man pages
mkdir -p %{{buildroot}}%{{_mandir}}/man1
install -p -m 644 man/man1/hashreport.1 %{{buildroot}}%{{_mandir}}/man1/

# Clean up empty directories
find %{{buildroot}} -type d -empty -delete

%files
%license LICENSE
%doc README.md
%{{_bindir}}/hashreport
%{{python3_sitelib}}/hashreport/
%{{python3_sitelib}}/hashreport-*.dist-info/
%{{_mandir}}/man1/hashreport.1*

%changelog
{changelog}
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

    # Make sure we include all runtime dependencies
    deps = ["click", "rich", "tomli", "tqdm", "typing-extensions", "psutil"]

    # These are needed during build but not included as runtime deps
    build_deps = [
        "pip",
        "setuptools",
        "wheel",
    ]

    # Parse changelog
    changelog_path = Path("CHANGELOG.md")
    changelog_entries = parse_changelog(changelog_path)
    if not changelog_entries:
        changelog_entries = [
            (
                metadata["version"],
                datetime.now().strftime("%Y-%m-%d"),
                "Initial release",
            )
        ]

    # Format the spec file with changelog
    spec_content = SPEC_TEMPLATE.format(
        name=metadata["name"],
        version=metadata["version"],
        summary=metadata["description"].split("\n")[0],
        description=metadata["description"],
        license=metadata["license"],
        url=metadata["urls"].get("Repository", ""),
        requires=format_dependencies(deps),
        build_requires=format_build_requires(build_deps),
        changelog=format_changelog_entries(
            changelog_entries,
            metadata["authors"][0].split("<")[0].strip(),
            metadata["version"],
        ),
    )

    # Write to file
    spec_file = Path(f"{metadata['name']}.spec")
    spec_file.write_text(spec_content)
    print(f"Generated spec file: {spec_file}")


if __name__ == "__main__":
    main()
