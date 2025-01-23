# **Project Scripts**

The scripts directory contains scripts that can be used for various common project actions. These scripts are intended to be run from the project root directory.

## **Run Script**

`scripts/run.sh`

The `run.sh` script is the main entry point for running project scripts, however, the scripts in the `actions` directory can also be run directly if desired.

### Options

The `run.sh` script provides a quick way to run various project actions. The following options are available:

- `test`: run tests with coverage
- `security`: check for security issues
- `lint`: lint the code
- `format`: format code
- `install`: install dependencies

### Usage

To run a specific action, use the following command:

```bash
bash scripts/run.sh [OPTION] [FLAGS]
```

## **Install Dependencies**

`scripts/install.sh`

Installs Poetry (if needed) and then installs project dependencies. The script can be run with the following command:

```bash
bash scripts/run.sh install
```
To automatically install all dependencies, use the `-a` or `--all` flag:

```bash
bash scripts/run.sh install -a
```

## **Testing with Coverage**

`scripts/actions/test.sh`

Lint the code and run tests with coverage. This script can be run with the following command:

```bash
bash scripts/run.sh test
```

## **Security Check**

`scripts/actions/security.sh`

Check for security vulnerabilities with Bandit. This script can be run with the following command:

```bash
bash scripts/run.sh security
```

## **Linting**

`scripts/actions/lint.sh`

Lint the code using flake8. This script can be run with the following command:

```bash
bash scripts/run.sh lint
```

## **Code Formatting**

`scripts/actions/format.sh`

Format code with Black and sort imports with isort. This script can be run with the following command:

```bash
bash scripts/run.sh format
```
