# **Project Scripts**

The scripts directory contains scripts that can be used for various common project actions. These scripts are intended to be run from the project root directory.

## **Main Scripts**

### **Run Script**

`scripts/run.sh`

The `run.sh` script is the main entry point for running project scripts. It provides both interactive and non-interactive modes for executing various project actions.

#### **Available Actions**

- `test`: Run tests with coverage
- `security`: Check for security vulnerabilities using bandit
- `lint`: Lint the code using flake8
- `format`: Format code with black and sort imports with isort
- `mkdocs`: Manage MkDocs documentation site
- `install`: Install project dependencies
- `setup-hooks`: Set up pre-commit hooks
- `pre-commit`: Run pre-commit hooks

#### **Usage**

**Interactive Mode:**
```bash
bash scripts/run.sh
```
This will display a menu to select an action.

**Non-Interactive Mode:**
```bash
bash scripts/run.sh [ACTION] [FLAGS]
```

**Examples:**
```bash
# Run tests
bash scripts/run.sh test

# Start documentation server
bash scripts/run.sh mkdocs serve

# Format code
bash scripts/run.sh format
```

### **Install Script**

`scripts/install.sh`

Installs project dependencies and sets up the development environment.

#### **Options**

- `-a`, `--all`: Install all dependencies including documentation dependencies
- `-h`, `--help`: Show help message

#### **Usage**

```bash
# Interactive installation
bash scripts/install.sh

# Install all dependencies
bash scripts/install.sh --all
```

## **Action Scripts**

The `scripts/actions/` directory contains individual scripts for specific tasks:

### **Test Script**

`scripts/actions/test.sh`

Runs linting and tests with coverage reporting.

```bash
bash scripts/actions/test.sh
```

### **Security Script**

`scripts/actions/security.sh`

Checks for security vulnerabilities using bandit.

```bash
bash scripts/actions/security.sh
```

### **Lint Script**

`scripts/actions/lint.sh`

Lints the code using flake8.

```bash
bash scripts/actions/lint.sh
```

### **Format Script**

`scripts/actions/format.sh`

Formats code with black and sorts imports with isort.

```bash
bash scripts/actions/format.sh
```

### **MkDocs Script**

`scripts/actions/mkdocs.sh`

Manages the MkDocs documentation site with multiple commands.

#### **Commands**

- `serve`: Start development server (default)
- `build`: Build static site
- `deploy`: Deploy to GitHub Pages
- `clean`: Clean build directory
- `help`: Show help message

#### **Usage**

```bash
# Start development server
bash scripts/actions/mkdocs.sh serve

# Build static site
bash scripts/actions/mkdocs.sh build

# Deploy to GitHub Pages
bash scripts/actions/mkdocs.sh deploy

# Clean build directory
bash scripts/actions/mkdocs.sh clean
```

### **Pre-commit Script**

`scripts/actions/pre-commit.sh`

Runs pre-commit hooks on staged files or all files.

#### **Options**

- `--all`: Run pre-commit on all files
- `-h`, `--help`: Show help message

#### **Usage**

```bash
# Run on staged files
bash scripts/actions/pre-commit.sh

# Run on all files
bash scripts/actions/pre-commit.sh --all
```

### **Setup Hooks Script**

`scripts/actions/setup-hooks.sh`

Sets up pre-commit hooks for development.

#### **Options**

- `--all`: Run pre-commit on all files after setup
- `-h`, `--help`: Show help message

#### **Usage**

```bash
# Basic setup
bash scripts/actions/setup-hooks.sh

# Setup and run on all files
bash scripts/actions/setup-hooks.sh --all
```

## **Common Functions**

`scripts/actions/common.sh`

Contains shared functions used by action scripts:

- `check_dependency`: Checks if a dependency is available and offers to install it

## **Development Workflow**

### **Initial Setup**

```bash
# Install dependencies
bash scripts/install.sh --all

# Set up pre-commit hooks
bash scripts/actions/setup-hooks.sh --all
```

### **Daily Development**

```bash
# Format code
bash scripts/run.sh format

# Run tests
bash scripts/run.sh test

# Check security
bash scripts/run.sh security
```

### **Documentation**

```bash
# Start documentation server
bash scripts/run.sh mkdocs serve

# Build documentation
bash scripts/run.sh mkdocs build

# Deploy documentation
bash scripts/run.sh mkdocs deploy
```
