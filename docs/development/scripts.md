# **Project Scripts**

The scripts directory contains scripts that can be used for various common project actions. These scripts are intended to be run from the project root directory.

## **Run Script**

`scripts/run.sh`

The `run.sh` script is the main entry point for running project scripts, however, the scripts in the `actions` directory can also be run directly if desired.

### Options

The `run.sh` script provides a quick way to run various project actions. The following options are available:

- `-h`, `--help`: show help message and exit
- `test`: run tests with coverage
- `security`: check for security issues
- `lint`: lint the code
- `format`: format code
- `install`: install dependencies
- `setup-hooks`: setup pre-commit hooks
- `pre-commit`: run pre-commit hooks

### Usage

**Interactive**

The `run.sh` script can also be run in interactive mode. To do this, simply run the script without any options:

```bash
bash scripts/run.sh
```

This will prompt you to select an action to run.

**Non-Interactive**

To run a specific action without being prompted, you can pass the action as an argument:

```bash
bash scripts/run.sh [OPTION] [FLAGS]
```

For example, to run tests with coverage:

```bash
bash scripts/run.sh test
```
