#!/bin/bash

set -euo pipefail

# Source common functions
. "$(dirname "$0")/common.sh"

show_help() {
    echo "Usage: $0 [-h] [--all]"
    echo
    echo "Set up pre-commit hooks for development."
    echo
    echo "Options:"
    echo "  -h, --help    Show this help message and exit"
    echo "  --all         Run pre-commit on all files after setup"
    echo
}

run_all=false

# Parse arguments
while [[ "$#" -gt 0 ]]; do
    case $1 in
        -h|--help) show_help; exit 0 ;;
        --all) run_all=true ;;
        *) echo "Unknown parameter: $1"; exit 1 ;;
    esac
    shift
done

echo "Setting up pre-commit hooks..."
check_dependency pre-commit

poetry run pre-commit install

if [ "$run_all" = true ]; then
    echo "Running pre-commit on all files..."
    poetry run pre-commit run --all-files
fi

echo "Pre-commit hooks setup complete!"
