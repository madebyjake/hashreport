# **Basic Usage**

## **Command Structure**

The basic command structure is:

```bash
hashreport scan [OPTIONS] DIRECTORY
```

## **Core Commands**

### Scanning a Directory

To scan a directory and generate a hash report:

```bash
hashreport scan /path/to/directory
```

### Choosing Hash Algorithm

You can specify which hash algorithm to use:

```bash
hashreport scan --algorithm sha256 /path/to/directory
```

To see available hash algorithms:

```bash
hashreport algorithms
```

### Output Formats

hashreport supports CSV (default) and JSON output formats:

```bash
# Generate CSV report (default)
hashreport scan -f csv /path/to/directory

# Generate JSON report
hashreport scan -f json /path/to/directory

# Generate both formats
hashreport scan -f csv -f json /path/to/directory
```

### Specifying Output Location

Control where reports are saved:

```bash
hashreport scan /path/to/directory -o /path/to/output/
```

## **Filtering Options**

### **Size Filters**

Filter files by size:

```bash
# Files larger than 1MB
hashreport scan --min-size 1MB /path/to/directory

# Files smaller than 1GB
hashreport scan --max-size 1GB /path/to/directory

# Files between 1MB and 1GB
hashreport scan --min-size 1MB --max-size 1GB /path/to/directory
```

### **Pattern Matching**

Include or exclude files by pattern:

```bash
# Include only .txt files
hashreport scan --include "*.txt" /path/to/directory

# Exclude .tmp files
hashreport scan --exclude "*.tmp" /path/to/directory

# Use regex patterns
hashreport scan --regex --include ".*\.txt$" /path/to/directory
```

### **Processing Control**

Control how files are processed:

```bash
# Limit number of files
hashreport scan --limit 100 /path/to/directory

# Disable recursive scanning
hashreport scan --no-recursive /path/to/directory
```

## **File Listing**

Generate a list of files without calculating hashes:

```bash
hashreport filelist /path/to/directory
```

## **Viewing Reports**

View report contents in a paginated format:

```bash
# View entire report
hashreport view hashreport_<timestamp>.csv

# Filter report entries
hashreport view hashreport_<timestamp>.csv -f "mydoc"
```

## **Comparing Reports**

Compare two reports to identify changes:

```bash
# View differences between reports
hashreport compare hashreport_<old>.csv hashreport_<new>.csv

# Save comparison results
hashreport compare hashreport_<old>.csv hashreport_<new>.csv -o /path/to/output/
```

The comparison will show:

- Modified files (hash changed)
- Moved files (same hash, different location)
- Added files (new in second report)
- Removed files (missing in second report)

## **Configuration Management**

hashreport settings can be managed using the `config` command:

### Initialize Settings

Create a default settings file:

```bash
# Create in default location (~/.config/hashreport/settings.toml)
hashreport config init

# Create in custom location
hashreport config init ./my-settings.toml
```

### View Settings

Display current configuration:

```bash
hashreport config show
```

### Edit Settings

Open settings in your default text editor:

```bash
hashreport config edit
```

The editor used is determined by:
1. $VISUAL environment variable
2. $EDITOR environment variable
3. Platform default (vi/vim on Unix, notepad on Windows)

Settings are automatically validated when saved.

## **Getting Help**

For detailed information about available options:

```bash
hashreport --help
hashreport scan --help
```
