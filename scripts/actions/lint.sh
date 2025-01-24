#!/bin/bash

set -euo pipefail  # Exit on error, unset variable, or pipe failure

. ./scripts/actions/common.sh

show_help() {
    echo "Usage: $0 [-h]"
    echo
    echo "Lints the code using flake8."
    echo
}

if [[ "${1:-}" == "-h" ]]; then
    show_help
    exit 0
fi

echo "Linting code..."
check_dependency flake8
poetry run flake8 . -v
echo "Done!"
