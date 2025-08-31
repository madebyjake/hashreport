#!/bin/bash

set -euo pipefail

# Change to the project's root directory
cd "$(dirname "$0")/../.."

# No need to source common.sh for this script

# Check if mkdocs is available (either globally or through poetry)
check_mkdocs() {
    if command -v "mkdocs" >/dev/null 2>&1; then
        MKDOCS_CMD="mkdocs"
        return 0
    elif command -v "poetry" >/dev/null 2>&1 && poetry show mkdocs >/dev/null 2>&1; then
        MKDOCS_CMD="poetry run mkdocs"
        return 0
    else
        echo "MkDocs is not available. Installing..."
        echo "1. Install globally: pip install mkdocs mkdocs-material"
        echo "2. Install via Poetry: poetry add mkdocs mkdocs-material"
        echo "3. Run install script: ./scripts/install.sh"
        echo
        read -r -p "Choose option (1-3) or press Enter to exit: " choice
        case $choice in
            1)
                pip install mkdocs mkdocs-material
                MKDOCS_CMD="mkdocs"
                ;;
            2)
                poetry add mkdocs mkdocs-material
                MKDOCS_CMD="poetry run mkdocs"
                ;;
            3)
                ./scripts/install.sh
                MKDOCS_CMD="mkdocs"
                ;;
            *)
                echo "Exiting..."
                exit 1
                ;;
        esac
    fi
}

# Check for mkdocs availability
check_mkdocs

show_help() {
    echo "Usage: $0 [command]"
    echo
    echo "Commands:"
    echo "  serve     Start development server (default)"
    echo "  build     Build static site"
    echo "  deploy    Deploy to GitHub Pages"
    echo "  clean     Clean build directory"
    echo "  help      Show this help message"
    echo
    echo "Examples:"
    echo "  $0 serve     # Start development server"
    echo "  $0 build     # Build static site"
    echo "  $0 deploy    # Deploy to GitHub Pages"
}

run_mkdocs() {
    case ${1:-serve} in
        serve)
            echo "Starting MkDocs development server..."
            echo "Site will be available at: http://127.0.0.1:8000"
            echo "Press Ctrl+C to stop the server"
            echo
            $MKDOCS_CMD serve
            ;;
        build)
            echo "Building static site..."
            $MKDOCS_CMD build
            echo "Site built successfully in 'site/' directory"
            ;;
        deploy)
            echo "Deploying to GitHub Pages..."
            $MKDOCS_CMD gh-deploy
            echo "Deployment completed successfully"
            ;;
        clean)
            echo "Cleaning build directory..."
            if [[ -d "site" ]]; then
                rm -rf site
                echo "Build directory cleaned"
            else
                echo "No build directory to clean"
            fi
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            echo "Unknown command: $1"
            show_help
            exit 1
            ;;
    esac
}

# Run the command
run_mkdocs "$@"
