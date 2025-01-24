#!/bin/bash

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
