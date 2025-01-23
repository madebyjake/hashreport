#!/bin/bash

set -euo pipefail  # Exit on error, unset variable, or pipe failure

# Change to the project's root directory
cd "$(dirname "$0")/.."

# Make scripts in the actions directory executable
if [ -d "scripts/actions" ]; then
    chmod +x scripts/actions/*.sh
fi

echo "Installing dependencies..."

install_all=false

# Parse command line arguments
while [[ "$#" -gt 0 ]]; do
  case $1 in
    -a|--all) install_all=true ;;
    *) echo "Unknown parameter passed: $1"; exit 1 ;;
  esac
  shift
done

install_poetry() {
  if ! command -v poetry >/dev/null 2>&1; then
    echo "Installing Poetry..."
    curl -sSL https://install.python-poetry.org | python3 -
    echo "Poetry installed successfully. You may need to restart your shell."
  fi
}

install_dependencies() {
  poetry install -v
  if $install_all; then
    poetry install -v --with docs
  else
    read -r -p "Do you want to install documentation dependencies as well? (y/n): " install_docs
    if [[ "$install_docs" == "y" ]]; then
      poetry install -v --with docs
    fi
  fi
}

install_poetry
install_dependencies

echo "Done!"

# Ensure the install script is executable
chmod +x "$0"
