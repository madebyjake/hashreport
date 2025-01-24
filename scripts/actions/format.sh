#!/bin/bash

set -euo pipefail  # Exit on error, unset variable, or pipe failure

. ./scripts/actions/common.sh

show_help() {
    echo "Usage: $0 [-h]"
    echo
    echo "Formats code with black and sorts imports with isort."
    echo
}

if [[ "${1:-}" == "-h" ]]; then
    show_help
    exit 0
fi

echo "Formatting code with black..."
check_dependency black
poetry run black . -v

echo "Sorting imports with isort..."
check_dependency isort
poetry run isort . -v --profile black
echo "Done!"
