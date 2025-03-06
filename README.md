# hashreport

[![Python](https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=fff)](https://www.python.org/)
[![Poetry](https://img.shields.io/badge/Poetry-5037E9?logo=python&logoColor=fff)](https://python-poetry.org/)
[![MkDocs](https://img.shields.io/badge/MkDocs-526CFE?logo=materialformkdocs&logoColor=fff)](https://www.mkdocs.org/)
[![License](https://img.shields.io/badge/License-AGPL%20v3.0-5C2D91?logo=gnu&logoColor=fff)](https://www.gnu.org/licenses/agpl-3.0.en.html)<br>
[![CodeQL](https://github.com/madebyjake/hashreport/actions/workflows/codeql.yml/badge.svg)](https://github.com/madebyjake/hashreport/actions/workflows/codeql.yml)
[![Test](https://github.com/madebyjake/hashreport/actions/workflows/test.yml/badge.svg)](https://github.com/madebyjake/hashreport/actions/workflows/test.yml)
[![Security](https://github.com/madebyjake/hashreport/actions/workflows/security.yml/badge.svg)](https://github.com/madebyjake/hashreport/actions/workflows/security.yml)

## Overview

**hashreport** is a command-line tool that generates comprehensive hash reports for files within a directory. The reports can be output in CSV or JSON formats and include detailed information such as the file name, path, size, hash algorithm, hash value, and last modified date. Designed for speed and efficiency, **hashreport** can handle large volumes of files and offers filtering options to include or exclude files based on size, type, or name patterns.

## Features

- Bulk hash generation for large directories
- Support for multiple hash algorithms using [hashlib](https://docs.python.org/3/library/hashlib.html)
- Multi-threaded processing for faster performance
- Output reports in CSV and JSON formats
- Filter files by size, type, and name patterns
- Option to provide a file list for inclusion or exclusion
- Recursive directory traversal to process nested folders
- Report viewer and comparison tool
- Email report upon completion using SMTP

## Installation

There are a two ways to install **hashreport** on your system. Choose the option that works best for you:

### Install with Pip

You can install **hashreport** using `pip` from the Python Package Index ([PyPI](https://pypi.org/project/hashreport/)):

```bash
pip install hashreport
```

### Install from Source

#### Prerequisites

- [Python 3](https://www.python.org/downloads/) (tested with 3.10+)
- [Git](https://git-scm.com/downloads) (optional)

#### 1. Download the Repository

Clone the repository to your local machine using Git and navigate to the project directory:

```bash
git clone https://github.com/madebyjake/hashreport.git && cd hashreport
```

Alternatively, you can download the repository as a ZIP file and extract it to a folder on your machine.

#### 2. Install Dependencies

First we'll install Poetry, a Python packaging and dependency management tool. There are a few ways to do this, but the recommended method is to use the installer script:

```bash
curl -sSL https://install.python-poetry.org | python3 -
```

Next, install the project dependencies using Poetry:

```bash
poetry install
```

#### 3. Run the Application

You can now run the application using Poetry:

```bash
poetry run hashreport --version
```

## License

This project is licensed under the **Affero General Public License v3.0** - see the [LICENSE](LICENSE) file for details.

## Issues and Feedback

Please report any issues or feedback on the [GitHub Issues](https://github.com/madebyjake/hashreport/issues) page.
