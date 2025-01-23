#!/bin/bash

set -euo pipefail  # Exit on error, unset variable, or pipe failure

check_dependency() {
    if ! command -v "$1" >/dev/null 2>&1; then
        echo "Dependency '$1' is missing. Run the install script? (y/n): "
        read -r answer
        if [[ "$answer" == "y" ]]; then
            ./scripts/install.sh
        else
            exit 1
        fi
    fi
}

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
poetry run bandit -r . -v
echo "Done!"
