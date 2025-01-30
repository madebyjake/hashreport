# **Command Reference**

## **Global Options**

These options are available for all commands:

| Option | Description |
|--------|-------------|
| `-h`, `--help` | Show help message and exit |
| `--version` | Show version information |

## **Scan Command Options**

The `scan` command is the primary command for generating hash reports. Here are all available options:

| Option | Default | Description |
|--------|---------|-------------|
| `DIRECTORY` | Required | Path to scan for files |
| `-o`, `--output` | Current directory | Output directory or file path |
| `-a`, `--algorithm` | md5 | Hash algorithm to use |
| `-f`, `--format` | csv | Output format(s) (csv, json) |
| `--min-size` | None | Minimum file size (e.g., 1MB) |
| `--max-size` | None | Maximum file size (e.g., 1GB) |
| `--include` | None | Include files matching pattern |
| `--exclude` | None | Exclude files matching pattern |
| `--regex` | False | Use regex for pattern matching |
| `--limit` | None | Limit number of files to process |
| `--recursive/--no-recursive` | True | Process subdirectories recursively |
| `--email` | None | Email address to send report to |
| `--smtp-host` | None | SMTP server host |
| `--smtp-port` | 587 | SMTP server port |
| `--smtp-user` | None | SMTP username |
| `--smtp-password` | None | SMTP password |
| `--test-email` | False | Test email configuration |

## **Size Format**

When using `--min-size` or `--max-size`, the following formats are supported:

| Unit | Example | Description |
|------|---------|-------------|
| B | 1024B | Bytes |
| KB | 500KB | Kilobytes |
| MB | 10MB | Megabytes |
| GB | 1GB | Gigabytes |

## **Pattern Matching**

### Glob Patterns (Default)
- `*` matches any characters
- `?` matches single character
- `[seq]` matches any character in seq
- `[!seq]` matches any character not in seq

### Regex Patterns
When using `--regex`:
- `.*` matches any characters
- `\.` matches literal dot
- `$` matches end of string
- `^` matches start of string
- `[0-9]` matches any digit

## **Examples**

```bash
# Basic scan with defaults
hashreport scan /path/to/directory

# Complex scan with multiple options
hashreport scan /path/to/directory \
  --algorithm sha256 \
  -f csv -f json \
  --min-size 1MB \
  --max-size 1GB \
  --include "*.pdf" \
  --exclude "*.tmp" \
  --limit 1000 \
  -o /path/to/output/report.csv

# Using regex pattern matching
hashreport scan /path/to/directory \
  --regex \
  --include ".*\d{8}.*\.txt$" \
  --exclude "^temp_.*"
```
