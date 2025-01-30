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

### **Pattern Matching Options**

Regex patterns are case-insensitive by default. For case-sensitive matching, use the appropriate regex syntax.

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
