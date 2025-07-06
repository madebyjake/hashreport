# **Installation Guide**

## **Installation Methods**

There are two ways to install **hashreport** on your system. Choose the option that works best for you:

### **Install with Pip**

You can install **hashreport** using `pip` from the Python Package Index ([PyPI](https://pypi.org/project/hashreport/)). This is the recommended method for most users:

```bash
pip install hashreport
```

You can upgrade **hashreport** using `pip` with the following commands:

```bash
# Upgrade to the latest version
pip install --upgrade hashreport

# Or upgrade to a specific version
pip install --upgrade hashreport==0.9.0
```

### **Install from Source**

#### 1. **Download the Repository**

Clone the repository to your local machine using Git and navigate to the project directory:

```bash
git clone https://github.com/madebyjake/hashreport.git && cd hashreport
```

Alternatively, you can download the repository as a ZIP file and extract it to a folder on your machine.

#### 2. **Install Dependencies**

First we'll install Poetry, a Python packaging and dependency management tool. There are a few ways to do this, but the recommended method is to use the installer script:

```bash
curl -sSL https://install.python-poetry.org | python3 -
```

Next, install the project dependencies using Poetry:

```bash
poetry install
```

#### 3. **Run the Application**

You can now run the application using Poetry:

```bash
poetry run hashreport --version
```

## **Verification**

After installation, verify that hashreport is working correctly:

```bash
# Check version
hashreport --version

# Run a test scan
hashreport scan --test /tmp
```

## **Next Steps**

After successful installation:

1. Review the [Quick Start Guide](basic.md#quick-start)
2. Learn about [Basic Usage](basic.md)
3. Explore [Advanced Features](advanced.md)
4. Configure your [Settings](advanced.md#configuration)

---

## **Troubleshooting**

### **Common Installation Issues**

#### **1. Python Version Issues**

If you see an error about Python version compatibility:

```bash
# Check your Python version
python3 --version

# If needed, install Python 3.10 or higher

## On Ubuntu/Debian:
sudo apt update && \
sudo apt install python3.10

## On Fedora/CentOS/RHEL:
sudo dnf update && \
sudo dnf install python3.10

## On macOS with Homebrew:
brew install python@3.10
```

#### **2. Permission Issues**

If you encounter permission errors:

```bash
# For pip installation
pip install --user hashreport

# For Poetry installation
poetry config virtualenvs.in-project true
```

#### **3. Poetry Installation Issues**

If Poetry installation fails:

```bash
# Try alternative installation method
python3 -m pip install poetry

# Or use pipx (recommended)
python3 -m pip install --user pipx
python3 -m pipx ensurepath
pipx install poetry
```

#### **4. Virtual Environment Issues**

If you have problems with virtual environments:

```bash
# Create a new virtual environment
python3 -m venv .venv

# Activate it
source .venv/bin/activate  # On Unix/macOS
.venv\Scripts\activate     # On Windows

# Install hashreport
pip install hashreport
```

### **Getting Help**

If you're still experiencing issues:

1. Check the [GitHub Issues](https://github.com/madebyjake/hashreport/issues) for known problems
2. Review the [Troubleshooting Guide](troubleshooting.md) for more detailed solutions
3. Create a new issue with:
   - Your operating system and version
   - Python version (`python3 --version`)
   - Full error message
   - Steps to reproduce the issue
