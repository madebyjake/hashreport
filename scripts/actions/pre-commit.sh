#!/bin/bash

set -euo pipefail

# Source common functions
. "$(dirname "$0")/common.sh"

show_help() {
    echo "Usage: $0 [-h] [--all]"
    echo
    echo "Run pre-commit hooks."
    echo
    echo "Options:"
    echo "  -h, --help    Show this help message and exit"
    echo "  --all         Run pre-commit on all files"
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

echo "Running pre-commit hooks..."
check_dependency pre-commit

if [ "$run_all" = true ]; then
    echo "Running pre-commit on all files..."
    poetry run pre-commit run --all-files
else
    poetry run pre-commit run
fi

echo "Pre-commit hooks run complete!"
