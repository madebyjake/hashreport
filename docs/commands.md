# **Command Reference**

This document provides detailed information about all available commands in hashreport.

## **Global Options**

| Option | Description |
|--------|-------------|
| `--help` | Show help message and exit |
| `--version` | Show version and exit |

## **Commands**

### **scan**

Generate a hash report for files in a directory.

```bash
hashreport scan [OPTIONS] DIRECTORY
```

#### **Options**

| Option | Default | Description |
|--------|---------|-------------|
| `DIRECTORY` | - | Directory to scan |
| `-a, --algorithm` | `sha256` | Hash algorithm to use |
| `-f, --format` | `csv` | Output format (csv, json) |
| `-o, --output` | - | Output directory |
| `-r, --recursive` | `True` | Scan directories recursively |
| `-i, --include` | - | Include files matching pattern |
| `-e, --exclude` | - | Exclude files matching pattern |
| `--regex` | `False` | Use regex patterns |
| `--min-size` | - | Minimum file size |
| `--max-size` | - | Maximum file size |
| `--limit` | - | Limit number of files |
| `--email` | - | Email address for report |
| `--smtp-host` | - | SMTP server host |
| `--smtp-port` | - | SMTP server port |
| `--smtp-user` | - | SMTP username |
| `--smtp-password` | - | SMTP password |
| `--test-email` | `False` | Test email configuration |

### **filelist**

Generate a list of files in a directory.

```bash
hashreport filelist [OPTIONS] DIRECTORY
```

#### **Options**

| Option | Default | Description |
|--------|---------|-------------|
| `DIRECTORY` | - | Directory to scan |
| `-r, --recursive` | `True` | Scan directories recursively |
| `-i, --include` | - | Include files matching pattern |
| `-e, --exclude` | - | Exclude files matching pattern |
| `--regex` | `False` | Use regex patterns |
| `--min-size` | - | Minimum file size |
| `--max-size` | - | Maximum file size |
| `--limit` | - | Limit number of files |

### **view**

View report contents.

```bash
hashreport view [OPTIONS] REPORT_FILE
```

#### **Options**

| Option | Default | Description |
|--------|---------|-------------|
| `REPORT_FILE` | - | Report file to view |
| `-f, --filter` | - | Filter entries by pattern |

### **compare**

Compare two report files.

```bash
hashreport compare [OPTIONS] OLD_REPORT NEW_REPORT
```

#### **Options**

| Option | Default | Description |
|--------|---------|-------------|
| `OLD_REPORT` | - | First report file |
| `NEW_REPORT` | - | Second report file |
| `-o, --output` | - | Output directory |

### **config**

Manage configuration settings.

```bash
hashreport config [OPTIONS] COMMAND
```

#### **Commands**

| Command | Description |
|---------|-------------|
| `show` | Display current configuration |
| `edit` | Edit configuration file |

### **algorithms**

List available hash algorithms.

```bash
hashreport algorithms
```

## **Examples**

### **Basic Usage**

```bash
# Scan directory with default settings
hashreport scan /path/to/directory

# Scan with specific algorithm
hashreport scan --algorithm sha512 /path/to/directory

# Generate multiple formats
hashreport scan -f csv -f json /path/to/directory
```

### **Advanced Usage**

```bash
# Scan with filters
hashreport scan \
  --include "*.pdf" \
  --exclude "*.tmp" \
  --min-size 1MB \
  --max-size 1GB \
  /path/to/directory

# Use regex patterns
hashreport scan \
  --regex \
  --include ".*\d{8}.*" \
  /path/to/directory

# Email report
hashreport scan \
  --email user@example.com \
  --smtp-host smtp.example.com \
  --smtp-user username \
  --smtp-password password \
  /path/to/directory
```

For more information, see:
- [Basic Usage](basic.md)
- [Advanced Usage](advanced.md)
- [Configuration Guide](configuration.md)
- [Troubleshooting](troubleshooting.md)
