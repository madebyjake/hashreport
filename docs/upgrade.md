# **Upgrade Guide**

## **Upgrade Methods**

There are several ways to upgrade **hashreport** to a new version. Choose the method that matches your original installation:

### **Upgrade with Pip**

If you installed **hashreport** using `pip`, you can upgrade it using the following commands:

```bash
# Upgrade to the latest version
pip install --upgrade hashreport

# Or upgrade to a specific version
pip install --upgrade hashreport==1.0.0

# Check current version before upgrading
hashreport --version

# Verify the upgrade was successful
hashreport --version
```

### **Upgrade from Source**

If you installed **hashreport** from source, you can upgrade by updating the repository and reinstalling:

#### 1. **Update the Repository**

Navigate to your hashreport directory and pull the latest changes:

```bash
cd /path/to/hashreport
git pull origin main
```

#### 2. **Update Dependencies**

Update the project dependencies using Poetry:

```bash
poetry update
```

#### 3. **Reinstall the Application**

Reinstall the application to ensure all changes are applied:

```bash
poetry install
```

#### 4. **Verify the Upgrade**

Check that the upgrade was successful:

```bash
poetry run hashreport --version
```

### **Upgrade with Poetry (Development)**

If you're using Poetry for development:

```bash
# Update dependencies
poetry update

# Reinstall the package
poetry install

# Verify version
poetry run hashreport --version
```

## **Version Checking**

Before upgrading, it's always good practice to check your current version:

```bash
# Check current version
hashreport --version

# Check available versions on PyPI
pip index versions hashreport
```

## **Pre-Upgrade Checklist**

Before upgrading, consider the following:

1. **Backup Configuration**: Save your current configuration files
2. **Check Compatibility**: Review the [changelog](https://github.com/madebyjake/hashreport/blob/main/CHANGELOG.md) for breaking changes
3. **Test Environment**: Consider testing the upgrade in a non-production environment first
4. **Dependencies**: Ensure your Python version meets the new requirements

## **Post-Upgrade Verification**

After upgrading, verify that everything is working correctly:

```bash
# Check version
hashreport --version

# Test basic functionality
hashreport scan --test /tmp

# Verify configuration still works
hashreport config --show
```

## **Next Steps**

After successful upgrade:

1. Review the [Changelog](https://github.com/madebyjake/hashreport/blob/main/CHANGELOG.md) for new features
2. Check [Configuration](configuration.md) for new options
3. Explore [Advanced Features](advanced.md) for new capabilities
4. Review [Troubleshooting](troubleshooting.md) if you encounter issues

---

## **Troubleshooting**

### **Common Upgrade Issues**

#### **1. Permission Errors**

If you encounter permission errors during upgrade:

```bash
# For pip installation
pip install --user --upgrade hashreport

# For Poetry installation
poetry config virtualenvs.in-project true
poetry install
```

#### **2. Dependency Conflicts**

If you see dependency conflicts:

```bash
# Check for conflicting packages
pip check

# Try upgrading with --force-reinstall
pip install --upgrade --force-reinstall hashreport

# For Poetry, try updating all dependencies
poetry update --all
```

#### **3. Version Compatibility Issues**

If the new version has compatibility issues:

```bash
# Downgrade to previous version
pip install --upgrade hashreport==0.9.0

# Or install a specific working version
pip install hashreport==0.8.5
```

#### **4. Configuration File Issues**

If your configuration files are no longer compatible:

```bash
# Backup old config
cp ~/.config/hashreport/config.toml ~/.config/hashreport/config.toml.backup

# Generate new default config
hashreport config --init

# Manually merge your custom settings
```

#### **5. Poetry Environment Issues**

If Poetry upgrade fails:

```bash
# Clear Poetry cache
poetry cache clear . --all

# Remove and recreate virtual environment
poetry env remove python
poetry install
```

### **Getting Help**

If you're still experiencing upgrade issues:

1. Check the [GitHub Issues](https://github.com/madebyjake/hashreport/issues) for known problems
2. Review the [Troubleshooting Guide](troubleshooting.md) for more detailed solutions
3. Check the [Changelog](https://github.com/madebyjake/hashreport/blob/main/CHANGELOG.md) for breaking changes
4. Create a new issue with:
   - Your current hashreport version
   - Target version you're trying to upgrade to
   - Your operating system and Python version
   - Full error message
   - Steps to reproduce the issue
