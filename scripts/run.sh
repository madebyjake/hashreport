#!/bin/bash

set -euo pipefail  # Exit on error, unset variable, or pipe failure

# Change to the project's root directory
cd "$(dirname "$0")/.."

# Make scripts in the actions directory executable
chmod +x ./scripts/actions/*.sh

show_help() {
    echo "Usage: $0 [-h] [script_name]"
    echo
    echo "Options:"
    echo "  -h                Show this help message"
    echo
    echo "Scripts:"
    echo "  test              Run tests with coverage"
    echo "  security          Check for security vulnerabilities"
    echo "  lint              Lint the code"
    echo "  format            Format the code"
    echo "  install           Run the install script"
}

run_script() {
    case $1 in
        test)
            ./scripts/actions/test.sh
            ;;
        security)
            ./scripts/actions/security.sh
            ;;
        lint)
            ./scripts/actions/lint.sh
            ;;
        format)
            ./scripts/actions/format.sh
            ;;
        install)
            ./scripts/install.sh
            ;;
        *)
            echo "Unknown script: $1"
            show_help
            exit 1
            ;;
    esac
}

interactive_mode() {
    echo "Choose a script to run:"
    echo "1: test"
    echo "2: security"
    echo "3: lint"
    echo "4: format"
    echo "5: install"
    read -r -p "Enter the number of your choice: " choice
    case $choice in
         1) run_script test ;;
         2) run_script security ;;
         3) run_script lint ;;
         4) run_script format ;;
         5) run_script install ;;
         *) echo "Invalid choice" ;;
    esac
}

if [[ $# -eq 0 ]]; then
    show_help
    exit 1
fi

case $1 in
    -h) show_help; exit 0 ;;
    -i) interactive_mode; exit 0 ;;
    *) run_script $1; exit 0 ;;
esac
