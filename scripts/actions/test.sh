#!/bin/bash

set -euo pipefail  # Exit on error, unset variable, or pipe failure

# Source the common script
. ./scripts/actions/common.sh

show_help() {
    echo "Usage: $0 [-h]"
    echo
    echo "Runs lint and then tests with coverage."
    echo
}

if [[ "${1:-}" == "-h" ]]; then
    show_help
    exit 0
fi

echo "Linting code..."
check_dependency flake8
poetry run flake8 . -v
echo "Linting done!"

echo "Running tests with coverage..."
check_dependency coverage
poetry run coverage run -m pytest -v
poetry run coverage report -m
echo "Done!"
