# **`hashreport`**

[![Python](https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=fff)](https://www.python.org/)
[![Poetry](https://img.shields.io/badge/Poetry-5037E9?logo=python&logoColor=fff)](https://python-poetry.org/)
[![MkDocs](https://img.shields.io/badge/MkDocs-526CFE?logo=materialformkdocs&logoColor=fff)](https://www.mkdocs.org/)
[![License](https://img.shields.io/badge/License-AGPL%20v3.0-5C2D91?logo=gnu&logoColor=fff)](https://www.gnu.org/licenses/agpl-3.0.en.html)<br>
[![CodeQL](https://github.com/madebyjake/hashreport/actions/workflows/codeql.yml/badge.svg)](https://github.com/madebyjake/hashreport/actions/workflows/codeql.yml)
[![Testing](https://github.com/madebyjake/hashreport/actions/workflows/test.yml/badge.svg)](https://github.com/madebyjake/hashreport/actions/workflows/test.yml)
[![Security](https://github.com/madebyjake/hashreport/actions/workflows/security.yml/badge.svg)](https://github.com/madebyjake/hashreport/actions/workflows/security.yml)

???+ warning

    This documentation site is an **early work in progress** and may contain errors and incomplete information.

## **Overview**

**hashreport** is a command-line tool that generates comprehensive hash reports for files within a directory. The reports can be output in CSV or JSON formats and include detailed information such as the file name, path, size, hash algorithm, hash value, and last modified date. Designed for speed and efficiency, **hashreport** can handle large volumes of files and offers filtering options to include or exclude files based on size, type, or name patterns.

## **Features**

- Bulk hash generation for large directories
- Support for multiple hash algorithms using [hashlib](https://docs.python.org/3/library/hashlib.html)
- Multi-threaded processing for faster performance
- Test run mode to process a subset of files
- Output reports in CSV and JSON formats
- Filter files by size, type, and name patterns
- Option to provide a file list for inclusion or exclusion
- Recursive directory traversal to process nested folders
- Email report upon completion using SMTP

## **Installation**

See the [Installation](getting-started/install.md) page for detailed instructions on how to install **hashreport**.

## **License**

This project is licensed under the [Affero General Public License v3.0](https://www.gnu.org/licenses/agpl-3.0.en.html).

## **Issues and Feedback**

Please report any issues or feedback on the [GitHub Issues](https://github.com/madebyjake/hashreport/issues) page.
