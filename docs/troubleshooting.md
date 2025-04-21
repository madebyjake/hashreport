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
```

## **Common Error Messages**

### **"File not found"**

**Solution**: Verify file path and permissions
```bash
ls -la /path/to/file
```

### **"Invalid hash algorithm"**

**Solution**: Check available algorithms
```bash
hashreport algorithms
```

## **Getting More Help**

If you're still experiencing issues:

1. **Check Logs**
   ```bash
   # Enable debug logging
   hashreport scan --debug /path/to/directory
   ```

2. **Create Issue**

    You can create an issue on [GitHub](https://github.com/madebyjake/hashreport/issues).

    Issues should include:

    - Any error messages
    - Any relevant logs
    - System information
    - Steps to reproduce
