#!/bin/bash

set -euo pipefail

# Change to the project's root directory
cd "$(dirname "$0")/../.."

# Source common functions
source ./scripts/actions/common.sh

# Check if mkdocs is installed
check_dependency "mkdocs"

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
            mkdocs serve
            ;;
        build)
            echo "Building static site..."
            mkdocs build
            echo "Site built successfully in 'site/' directory"
            ;;
        deploy)
            echo "Deploying to GitHub Pages..."
            mkdocs gh-deploy
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
