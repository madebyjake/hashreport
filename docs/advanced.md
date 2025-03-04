# **Advanced Usage**

## **Regular Expressions**

While the basic glob patterns work for simple cases, regex provides more powerful pattern matching capabilities.

### **Pattern Examples**

Use the `--regex` flag with `--include` or `--exclude`:

```bash
# Match files ending in numbers
hashreport scan --regex --include ".*[0-9]$" /path/to/directory

# Match specific date formats in filenames
hashreport scan --regex --include ".*\d{4}-\d{2}-\d{2}.*" /path/to/directory

# Exclude files with specific patterns
hashreport scan --regex --exclude "^(backup|temp).*" /path/to/directory

# Multiple patterns
hashreport scan --regex \
  --include ".*\.(jpg|png)$" \
  --exclude "thumb.*\.jpg$" \
  /path/to/directory
```

### **Filelist with Patterns**

The filelist command supports the same pattern matching:

## **Email Notifications**

hashreport can email reports upon completion using SMTP.

### **Basic Email Setup**

```bash
hashreport scan /path/to/directory \
  --email recipient@example.com \
  --smtp-host smtp.example.com \
  --smtp-user username \
  --smtp-password password
```

### **Testing Email Configuration**

Test your email settings without processing files:

```bash
hashreport scan /path/to/directory \
  --email recipient@example.com \
  --smtp-host smtp.example.com \
  --smtp-user username \
  --smtp-password password \
  --test-email
```

### **Gmail Example**

Using Gmail's SMTP server:

```bash
hashreport scan /path/to/directory \
  --email recipient@gmail.com \
  --smtp-host smtp.gmail.com \
  --smtp-port 587 \
  --smtp-user your.email@gmail.com \
  --smtp-password "your-app-password"
```

!!! note
    For Gmail, you'll need to use an App Password if you have 2-factor authentication enabled.
    Generate one at: Google Account → Security → 2-Step Verification → App passwords

### **Environment Variables**

You can store SMTP credentials in environment variables:

```bash
export HASHREPORT_SMTP_HOST=smtp.example.com
export HASHREPORT_SMTP_USER=username
export HASHREPORT_SMTP_PASSWORD=password

# Now run without exposing credentials in command
hashreport scan /path/to/directory --email recipient@example.com
```

## **Performance Tuning**

### **Worker Threads**

hashreport automatically uses multiple threads based on your CPU cores. You can override this in the configuration:

```toml
# pyproject.toml
[tool.hashreport]
max_workers = 4  # Set specific number of worker threads
```

### **Chunk Size**

For large files, you can adjust the chunk size used when calculating hashes:

```toml
# pyproject.toml
[tool.hashreport]
chunk_size = 8192  # Default is 4096
```

## **Custom Report Names**

### **Timestamp Format**

Customize the timestamp format used in report filenames:

```toml
# pyproject.toml
[tool.hashreport]
timestamp_format = "%Y%m%d_%H%M%S"  # Default is "%y%m%d-%H%M"
```

### **Output Examples**

```bash
# Custom named reports
hashreport scan /path/to/directory -o custom_report.csv

# Multiple formats with custom names
hashreport scan /path/to/directory \
  -o report.csv \
  -f csv -f json
```

## **Report Comparison**

### **Understanding Changes**

The comparison functionality identifies several types of changes:

- **Modified**: File exists in both reports but has different hash values
- **Moved**: Same file (identical hash) exists in different locations
- **Added**: File exists only in the newer report
- **Removed**: File exists only in the older report

### **Output Format**

Changes are displayed with bold text for better visibility:

- Change type is displayed in **bold**
- File paths show the original and new locations
- Details include hash values and change descriptions
- Complete path information is shown in separate columns

### **Saving Comparisons**

Comparison results can be saved to CSV format:

```bash
hashreport compare old_report.csv new_report.csv -o /path/to/output/
```

The output filename will be generated automatically using the format:
`compare_<old_report>_<new_report>.csv`

### **Using with Version Control**

Example workflow for tracking file changes:

```bash
# Generate baseline report
hashreport scan /project/dir -o baseline.csv

# Later, generate new report
hashreport scan /project/dir -o current.csv

# Compare changes
hashreport compare baseline.csv current.csv
```
