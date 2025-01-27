#!/bin/bash

set -euo pipefail  # Exit on error, unset variable, or pipe failure

. ./scripts/actions/common.sh

show_help() {
    echo "Usage: $0 [-h]"
    echo
    echo "Checks for security vulnerabilities using bandit."
    echo
}

if [[ "${1:-}" == "-h" ]]; then
    show_help
    exit 0
fi

echo "Checking for security vulnerabilities..."
check_dependency bandit
poetry run bandit -r . -c .bandit.yaml -v
echo "Done!"
