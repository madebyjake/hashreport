# **Troubleshooting Guide**

This guide helps you resolve common issues with hashreport. If you're still experiencing problems, please check the [GitHub Issues](https://github.com/madebyjake/hashreport/issues) or create a new issue.

## **Installation Issues**

### **Python Version Compatibility**

**Problem**: Error about Python version compatibility
**Solution**: Ensure you're using Python 3.10 or higher

```bash
# Check Python version
python3 --version

# Install Python 3.10 or higher on macOS
brew install python@3.10

# Install Python 3.10 or higher on Ubuntu/Debian
sudo apt install python3.10

# Install Python 3.10 or higher on Fedora/CentOS/RHEL
sudo dnf install python3.10
```

### **Poetry Installation**

**Problem**: Poetry installation fails
**Solution**: Try alternative installation methods

```bash
# Install with pip
python3 -m pip install poetry

# Or use pipx (recommended)
python3 -m pip install --user pipx
python3 -m pipx ensurepath
pipx install poetry
```

### **Permission Issues**

**Problem**: Permission denied during installation
**Solution**: Use user installation or virtual environment

```bash
# Install for current user only
pip install --user hashreport

# Or use virtual environment
python3 -m venv hashreport_env
source hashreport_env/bin/activate  # On Unix/macOS
hashreport_env\Scripts\activate     # On Windows
pip install hashreport
```

## **File Access Issues**

### **Permission Denied**

**Problem**: Cannot access files or directories
**Solution**: Check file permissions

```bash
# Check directory permissions
ls -la /path/to/directory

# Check file permissions
ls -la /path/to/file

# Fix permissions if needed
chmod 644 /path/to/file
chmod 755 /path/to/directory
```

### **Path Issues**

**Problem**: Invalid or inaccessible paths
**Solution**: Verify path format and existence

```bash
# Use absolute paths
hashreport scan /absolute/path/to/directory

# Check path existence
ls /path/to/directory

# Handle spaces in paths
hashreport scan "/path/with spaces/directory"

# Handle special characters
hashreport scan "/path/with\*special\?chars/"
```

### **Symbolic Links**

**Problem**: Issues with symbolic links
**Solution**: Check link validity and permissions

```bash
# Check if symbolic link is valid
ls -la /path/to/symlink

# Follow symbolic links manually
hashreport scan $(readlink -f /path/to/symlink)

# Or scan the target directory directly
hashreport scan /actual/target/directory
```

## **Memory and Performance Issues**

### **Out of Memory**

**Problem**: Process runs out of memory
**Solution**: Adjust memory settings

```toml
# ~/.config/hashreport/settings.toml
[hashreport]
# Reduce memory usage
memory_threshold = 0.70  # Lower threshold
batch_size = 500         # Smaller batches
chunk_size = 2048        # Smaller chunks
mmap_threshold = 5242880 # 5MB - Use mmap for smaller files
```

### **Slow Performance**

**Problem**: Processing is very slow
**Solution**: Optimize settings for your system

```toml
# ~/.config/hashreport/settings.toml
[hashreport]
# Increase performance
max_workers = 8          # More workers
batch_size = 2000        # Larger batches
resource_check_interval = 2.0  # Less frequent checks
```

### **High CPU Usage**

**Problem**: Excessive CPU usage
**Solution**: Reduce worker count and adjust settings

```toml
# ~/.config/hashreport/settings.toml
[hashreport]
# Reduce CPU usage
max_workers = 4          # Fewer workers
min_workers = 1          # Lower minimum
resource_check_interval = 5.0  # Less frequent monitoring
```

## **Email Issues**

### **SMTP Connection Failed**

**Problem**: Cannot connect to SMTP server
**Solution**: Check SMTP settings

```bash
# Test SMTP connection
hashreport scan /tmp --test-email \
  --email test@example.com \
  --smtp-host smtp.example.com \
  --smtp-port 587 \
  --smtp-tls

# Common SMTP settings
# Gmail: smtp.gmail.com:587 (TLS)
# Outlook: smtp-mail.outlook.com:587 (TLS)
# Yahoo: smtp.mail.yahoo.com:587 (TLS)
```

### **Authentication Failed**

**Problem**: SMTP authentication error
**Solution**: Check credentials and use app passwords

```bash
# For Gmail, use App Passwords
# 1. Enable 2-factor authentication
# 2. Generate app password at: Google Account → Security → App passwords
# 3. Use app password instead of account password

hashreport scan /path/to/directory \
  --email recipient@gmail.com \
  --smtp-host smtp.gmail.com \
  --smtp-port 587 \
  --smtp-user your.email@gmail.com \
  --smtp-password "your-app-password" \
  --smtp-tls
```

### **Email Not Sent**

**Problem**: No error but email not received
**Solution**: Check spam folder and email settings

```bash
# Test with verbose output
hashreport scan /tmp --test-email \
  --email test@example.com \
  --smtp-host smtp.example.com \
  --smtp-user username \
  --smtp-password password \
  --smtp-tls

# Check email server logs if available
```

## **Report Generation Issues**

### **Invalid Report Format**

**Problem**: Error creating report file
**Solution**: Check output directory and permissions

```bash
# Ensure output directory exists
mkdir -p /path/to/output

# Check write permissions
ls -la /path/to/output

# Use absolute paths
hashreport scan /path/to/directory -o /absolute/path/to/report.csv
```

### **Large Report Files**

**Problem**: Reports are too large to handle
**Solution**: Use filtering and limits

```bash
# Limit number of files
hashreport scan /path/to/directory --limit 1000

# Filter by file type
hashreport scan /path/to/directory --include "*.pdf"

# Filter by size
hashreport scan /path/to/directory --min-size 1KB --max-size 100MB
```

### **Report Comparison Issues**

**Problem**: Cannot compare reports
**Solution**: Check report format and structure

```bash
# Verify report files exist
ls -la report1.csv report2.csv

# Check report format
head -5 report1.csv

# Ensure reports have same structure
hashreport view report1.csv
hashreport view report2.csv
```

## **Configuration Issues**

### **Invalid Configuration**

**Problem**: Configuration validation errors
**Solution**: Check and fix configuration

```bash
# View current configuration
hashreport config show

# Edit configuration
hashreport config edit

# Reset to defaults (backup first)
cp ~/.config/hashreport/settings.toml ~/.config/hashreport/settings.toml.backup
rm ~/.config/hashreport/settings.toml
hashreport config show  # Creates new default config
```

### **Configuration Not Found**

**Problem**: Configuration file not found
**Solution**: Create configuration directory

```bash
# Create configuration directory
mkdir -p ~/.config/hashreport

# Generate default configuration
hashreport config show

# Or copy default configuration
cp /path/to/hashreport/default_config.toml ~/.config/hashreport/settings.toml
```

## **Pattern Matching Issues**

### **Invalid Regex Patterns**

**Problem**: Regex pattern errors
**Solution**: Test and fix patterns

```bash
# Test regex pattern in Python
python3 -c "import re; re.compile('.*\\.txt$')"

# Use simpler patterns
hashreport scan /path/to/directory --include "*.txt"

# Escape special characters
hashreport scan /path/to/directory --regex --include ".*\\.txt$"
```

### **Pattern Not Matching**

**Problem**: Expected files not included/excluded
**Solution**: Check pattern syntax and test

```bash
# Test pattern with filelist command
hashreport filelist /path/to/directory --include "*.pdf"

# Use verbose output to see what's being processed
hashreport scan /path/to/directory --include "*.pdf" --limit 10
```

## **Threading and Concurrency Issues**

### **Too Many Open Files**

**Problem**: "Too many open files" error
**Solution**: Reduce worker count and batch size

```toml
# ~/.config/hashreport/settings.toml
[hashreport]
# Reduce file handles
max_workers = 4          # Fewer workers
batch_size = 100         # Smaller batches
```

### **Thread Pool Exhaustion**

**Problem**: Thread pool errors
**Solution**: Adjust thread settings

```toml
# ~/.config/hashreport/settings.toml
[hashreport]
# Adjust thread settings
min_workers = 1          # Lower minimum
max_workers = 4          # Lower maximum
resource_check_interval = 2.0  # Less frequent checks
```

## **Common Error Messages**

### **"File not found"**

**Solution**: Verify file path and permissions
```bash
ls -la /path/to/file
file /path/to/file
```

### **"Invalid hash algorithm"**

**Solution**: Check available algorithms
```bash
hashreport algorithms
```

### **"Permission denied"**

**Solution**: Check file and directory permissions
```bash
ls -la /path/to/directory
chmod 755 /path/to/directory
```

### **"Memory error"**

**Solution**: Reduce memory usage
```toml
# ~/.config/hashreport/settings.toml
[hashreport]
memory_threshold = 0.70
batch_size = 500
```

### **"Timeout error"**

**Solution**: Increase timeout settings
```toml
# ~/.config/hashreport/settings.toml
[hashreport.email_defaults]
timeout = 60  # Increase timeout
```

## **Platform-Specific Issues**

### **Windows Issues**

**Problem**: Path separator issues
**Solution**: Use proper path format

```bash
# Use forward slashes or escaped backslashes
hashreport scan C:/path/to/directory
hashreport scan "C:\\path\\to\\directory"
```

### **macOS Issues**

**Problem**: Permission issues with system directories
**Solution**: Grant necessary permissions

```bash
# Grant full disk access to terminal
# System Preferences → Security & Privacy → Privacy → Full Disk Access

# Or use user directories
hashreport scan ~/Documents
```

### **Linux Issues**

**Problem**: SELinux or AppArmor restrictions
**Solution**: Check security policies

```bash
# Check SELinux status
sestatus

# Check AppArmor status
aa-status

# Temporarily disable if needed (not recommended for production)
```

## **Getting More Help**

### **Enable Debug Logging**

```bash
# Set debug level
export HASHREPORT_LOG_LEVEL=DEBUG

# Run with debug output
hashreport scan /path/to/directory
```

### **Create Detailed Issue Report**

When creating an issue, include:

1. **System Information**
   ```bash
   uname -a
   python3 --version
   hashreport --version
   ```

2. **Error Messages**
   - Full error output
   - Any log files
   - Stack traces

3. **Steps to Reproduce**
   - Exact commands used
   - File structure
   - Expected vs actual behavior

4. **Configuration**
   ```bash
   hashreport config show
   ```

### **Useful Debugging Commands**

```bash
# Test basic functionality
hashreport --version
hashreport algorithms

# Test file access
hashreport filelist /tmp --limit 5

# Test report generation
hashreport scan /tmp --limit 1

# Test configuration
hashreport config show
```

### **Community Resources**

- [GitHub Issues](https://github.com/madebyjake/hashreport/issues)
- [GitHub Discussions](https://github.com/madebyjake/hashreport/discussions)
- [Documentation](https://madebyjake.github.io/hashreport/)

## **Performance Optimization**

### **For Large Directories**

```toml
# ~/.config/hashreport/settings.toml
[hashreport]
# Optimize for large directories
max_workers = 8
batch_size = 2000
memory_threshold = 0.90
mmap_threshold = 20971520  # 20MB
```

### **For Small Files**

```toml
# ~/.config/hashreport/settings.toml
[hashreport]
# Optimize for many small files
max_workers = 4
batch_size = 500
chunk_size = 1024
mmap_threshold = 1048576   # 1MB
```

### **For Network Drives**

```toml
# ~/.config/hashreport/settings.toml
[hashreport]
# Optimize for network drives
max_workers = 2
batch_size = 100
chunk_size = 8192
resource_check_interval = 5.0
```
