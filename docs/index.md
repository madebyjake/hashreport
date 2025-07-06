# **`hashreport`**

[![Python](https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=fff)](https://www.python.org/)
[![Poetry](https://img.shields.io/badge/Poetry-5037E9?logo=python&logoColor=fff)](https://python-poetry.org/)
[![MkDocs](https://img.shields.io/badge/MkDocs-526CFE?logo=materialformkdocs&logoColor=fff)](https://www.mkdocs.org/)
[![License](https://img.shields.io/badge/License-AGPL%20v3.0-5C2D91?logo=gnu&logoColor=fff)](https://www.gnu.org/licenses/agpl-3.0.en.html)<br>
[![CodeQL](https://github.com/madebyjake/hashreport/actions/workflows/codeql.yml/badge.svg)](https://github.com/madebyjake/hashreport/actions/workflows/codeql.yml)
[![Testing](https://github.com/madebyjake/hashreport/actions/workflows/test.yml/badge.svg)](https://github.com/madebyjake/hashreport/actions/workflows/test.yml)
[![Security](https://github.com/madebyjake/hashreport/actions/workflows/security.yml/badge.svg)](https://github.com/madebyjake/hashreport/actions/workflows/security.yml)

## **Overview**

**hashreport** is a command-line tool that generates comprehensive hash reports for files within a directory. The reports can be output in CSV or JSON formats and include detailed information such as the file name, path, size, hash algorithm, hash value, and last modified date. Designed for speed and efficiency, **hashreport** can handle large volumes of files and offers filtering options to include or exclude files based on size, type, or name patterns.

!!! info "Beta Release"
    This project is currently in beta. While feature-complete and well-tested, please report any issues you encounter.

## **Quick Start**

```bash
# Install hashreport
pip install hashreport

# Generate a hash report
hashreport scan /path/to/directory
```

See the [Workflow Overview](workflow.md) for a complete guide to using hashreport.

## **Quick Links**

- [Installation](install.md) - Get started with hashreport
- [Upgrading](upgrading.md) - Update to the latest version
- [Basic Usage](basic.md) - Basic usage examples
- [Advanced Usage](advanced.md) - Advanced features and options
- [Command Reference](commands.md) - Detailed command documentation
- [Configuration](configuration.md) - Customize hashreport
- [Troubleshooting](troubleshooting.md) - Common issues and solutions

## **Features**

### 🚀 **Core Features**
- Multi-threaded processing for fast bulk hash generation
- Support for multiple hash algorithms (MD5, SHA-256, etc.)
- Recursive directory traversal
- Comprehensive file information in reports

### 📊 **Output Options**
- CSV and JSON report formats
- Customizable output location
- Report viewer and comparison tool
- Email report delivery via SMTP

### 🔍 **Filtering Capabilities**
- Filter by file size (min/max)
- Filter by file type and name patterns
- Include/exclude file lists
- Processing limits and controls

## **Getting Started**

1. [Installation](install.md) - Set up hashreport on your system
2. [Basic Usage](basic.md) - Learn the fundamentals
3. [Command Reference](commands.md) - Detailed command documentation

## **Common Use Cases**

### 🔒 **File Integrity Checking**
- Generate baseline reports
- Monitor for changes
- Verify file integrity

### 🛡️ **Security Auditing**
- Scan sensitive files
- Track modifications
- Generate audit trails

### 💾 **Backup Verification**
- Verify backup integrity
- Compare file states
- Document changes

## **Additional Resources**

- [Contributing Guidelines](contributing.md) - Help improve hashreport
- [Project Scripts](scripts.md) - Development and maintenance tools

## **License**

This project is licensed under the [Affero General Public License v3.0](https://www.gnu.org/licenses/agpl-3.0.en.html).

## **Issues and Feedback**

Please report any issues or feedback on the [GitHub Issues](https://github.com/madebyjake/hashreport/issues) page.
