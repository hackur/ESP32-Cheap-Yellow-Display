#!/usr/bin/env bash
# CYD Stopwatch Development Helper

set -euo pipefail

cd "$(dirname "${BASH_SOURCE[0]}")"

case "${1:-help}" in
    "test")
        echo "Running tests..."
        uv run python test_stopwatch.py
        ;;
    "demo")
        echo "Running demo..."
        uv run python demo.py
        ;;
    "device-test")
        if [ -z "${2:-}" ]; then
            echo "Testing all devices..."
            uv run python test_device.py --scan --test-all
        else
            echo "Testing device $2..."
            uv run python test_device.py --port "$2"
        fi
        ;;
    "verify")
        if [ -z "${2:-}" ]; then
            echo "Error: Port required for verification"
            echo "Usage: $0 verify /dev/ttyUSB0"
            exit 1
        else
            echo "Verifying deployment on $2..."
            uv run python verify_deployment.py --port "$2"
        fi
        ;;
    "scan")
        echo "Scanning for CYD devices..."
        uv run python test_device.py --scan
        ;;
    "format")
        echo "Formatting code..."
        uv run black *.py
        uv run ruff check --fix *.py
        ;;
    "lint")
        echo "Linting code..."
        uv run ruff check *.py
        uv run mypy *.py --ignore-missing-imports
        ;;
    "clean")
        echo "Cleaning up..."
        rm -rf .venv __pycache__ .pytest_cache .mypy_cache
        rm -rf deploy lib
        ;;
    "install")
        echo "Installing dependencies..."
        uv sync
        ;;
    "update")
        echo "Updating dependencies..."
        uv sync --upgrade
        ;;
    "shell")
        echo "Activating development shell..."
        echo "Use 'exit' to leave the shell"
        uv run bash
        ;;
    *)
        echo "CYD Stopwatch Development Helper"
        echo "Usage: $0 {test|demo|device-test|verify|scan|format|lint|clean|install|update|shell}"
        echo ""
        echo "Commands:"
        echo "  test         - Run test suite"
        echo "  demo         - Run interactive demo" 
        echo "  device-test  - Test CYD device connection"
        echo "               - device-test [PORT] to test specific port"
        echo "  verify       - Verify deployment on device"
        echo "               - verify PORT to check deployment"
        echo "  scan         - Scan for available CYD devices"
        echo "  format       - Format code with black and ruff"
        echo "  lint         - Run linting with ruff and mypy"
        echo "  clean        - Clean up generated files"
        echo "  install      - Install dependencies"
        echo "  update       - Update dependencies"
        echo "  shell        - Enter development shell with all tools available"
        echo ""
        echo "Examples:"
        echo "  $0 scan                    # Find CYD devices"
        echo "  $0 device-test /dev/ttyUSB0    # Test device connection"
        echo "  $0 verify /dev/ttyUSB0         # Verify deployment"
        ;;
esac
