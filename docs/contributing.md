# **Contributing Guidelines**

Thank you for your interest in contributing to hashreport! This document provides guidelines and instructions for contributing to the project.

## **Development Environment Setup**

### **Prerequisites**

- Python 3.10 or higher (up to 3.14)
- Git
- Poetry (Python package manager)
- Pre-commit hooks

### **Setting Up the Development Environment**

1. **Clone the Repository**
   ```bash
   git clone https://github.com/madebyjake/hashreport.git
   cd hashreport
   ```

2. **Install Poetry**
   ```bash
   curl -sSL https://install.python-poetry.org | python3 -
   ```

3. **Install Dependencies**
   ```bash
   poetry install
   ```

4. **Set Up Pre-commit Hooks**
   ```bash
   poetry run pre-commit install
   ```

5. **Verify Setup**
   ```bash
   poetry run pytest
   ```

## **Running Tests**

### **Running All Tests**

```bash
# Run tests with coverage
poetry run pytest --cov=hashreport

# Run tests without coverage
poetry run pytest

# Run tests with verbose output
poetry run pytest -v
```

### **Running Specific Tests**

```bash
# Run a specific test file
poetry run pytest tests/test_scanner.py

# Run a specific test function
poetry run pytest tests/test_scanner.py::test_scan_directory

# Run tests matching a pattern
poetry run pytest -k "test_scan"
```

### **Test Coverage**

```bash
# Generate coverage report
poetry run pytest --cov=hashreport --cov-report=html

# View coverage in browser
open htmlcov/index.html
```

## **Code Style**

### **Formatting**

We use Black for code formatting:

```bash
# Format all Python files
poetry run black .

# Format a specific file
poetry run black hashreport/cli.py
```

### **Linting**

We use Flake8 for linting:

```bash
# Lint all Python files
poetry run flake8

# Lint a specific file
poetry run flake8 hashreport/cli.py
```

## **Making Changes**

### **1. Create a Branch**

```bash
# Create and switch to a new branch
git checkout -b feature/your-feature-name

# Or create a bug fix branch
git checkout -b fix/your-bug-fix
```

### **2. Make Your Changes**

- Write clear, concise code
- Add tests for new features
- Update documentation
- Follow the code style guidelines

### **3. Commit Your Changes**

We use conventional commits:

```bash
# Format: type(scope): description
git commit -m "feat(scanner): add memory-mapped file support"
```

**Types:**

| Type | Description |
|------|-------------|
| `feat` | New feature |
| `fix` | Bug fix |
| `docs` | Documentation changes |
| `style` | Code style changes |
| `refactor` | Code refactoring |
| `test` | Test changes |
| `chore` | Maintenance tasks |

### **4. Push Your Changes**

```bash
git push origin feature/your-feature-name
```

### **5. Create a Pull Request**

1. Go to the GitHub repository
2. Click "New Pull Request"
3. Select your branch
4. Fill in the PR template
5. Submit the PR

## **Documentation**

### **Updating Documentation**

1. **Update Source Code Documentation**
      - Add docstrings to new functions
      - Update existing docstrings
      - Follow Google style guide

2. **Update User Documentation**
      - Edit files in the `docs/` directory
      - Update examples
      - Add new features to relevant sections

3. **Build Documentation**
   ```bash
   poetry run mkdocs build
   ```

4. **Preview Documentation**
   ```bash
   poetry run mkdocs serve
   ```

## **Getting Help**

- Check the [GitHub Issues](https://github.com/madebyjake/hashreport/issues)
- Join the [Discussions](https://github.com/madebyjake/hashreport/discussions)
- Contact the maintainers

## **License**

By contributing, you agree that your contributions will be licensed under the project's [AGPL-3.0 License](LICENSE).
