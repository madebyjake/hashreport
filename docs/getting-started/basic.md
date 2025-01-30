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

## **Getting Help**

For detailed information about available options:

```bash
hashreport --help
hashreport scan --help
```
