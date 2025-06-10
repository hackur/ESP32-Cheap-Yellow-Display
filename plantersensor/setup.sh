#!/usr/bin/env bash
"""
CYD Stopwatch - Universal Installer
===================================

This installer sets up a complete development and deployment environment
for the CYD Stopwatch application using modern Python tooling.

Features:
- Uses uv for fast Python package management
- Installs all required command-line tools
- Downloads MicroPython libraries
- Creates deployment package
- Provides deployment instructions

Requirements: macOS, Linux, or Windows with bash/zsh
"""

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="cyd-stopwatch"
PYTHON_VERSION="3.11"
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="${PROJECT_DIR}/.venv"
DEPLOY_DIR="${PROJECT_DIR}/deploy"
LIB_DIR="${PROJECT_DIR}/lib"

# Utility functions
print_header() {
    echo -e "\n${PURPLE}========================================${NC}"
    echo -e "${PURPLE} $1${NC}"
    echo -e "${PURPLE}========================================${NC}\n"
}

print_step() {
    echo -e "${CYAN}➤ $1${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Detect operating system
detect_os() {
    case "$(uname -s)" in
        Darwin*) echo "macos" ;;
        Linux*)  echo "linux" ;;
        CYGWIN*|MINGW*|MSYS*) echo "windows" ;;
        *) echo "unknown" ;;
    esac
}

# Install uv if not present
install_uv() {
    print_step "Checking for uv package manager..."
    
    if command_exists uv; then
        print_success "uv is already installed"
        uv --version
        return 0
    fi
    
    print_step "Installing uv package manager..."
    
    case "$(detect_os)" in
        "macos")
            if command_exists brew; then
                brew install uv
            else
                curl -LsSf https://astral.sh/uv/install.sh | sh
                export PATH="$HOME/.cargo/bin:$PATH"
            fi
            ;;
        "linux")
            curl -LsSf https://astral.sh/uv/install.sh | sh
            export PATH="$HOME/.cargo/bin:$PATH"
            ;;
        "windows")
            powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
            ;;
        *)
            print_error "Unsupported operating system"
            exit 1
            ;;
    esac
    
    # Verify installation
    if command_exists uv; then
        print_success "uv installed successfully"
        uv --version
    else
        print_error "Failed to install uv. Please install manually from https://docs.astral.sh/uv/"
        exit 1
    fi
}

# Install system dependencies
install_system_deps() {
    print_step "Installing system dependencies..."
    
    local os_type=$(detect_os)
    
    case "$os_type" in
        "macos")
            if command_exists brew; then
                print_step "Installing dependencies via Homebrew..."
                brew install --quiet curl wget git || true
            else
                print_warning "Homebrew not found. Some dependencies may need manual installation."
            fi
            ;;
        "linux")
            if command_exists apt; then
                print_step "Installing dependencies via apt..."
                sudo apt update -qq
                sudo apt install -y curl wget git python3-dev python3-pip
            elif command_exists yum; then
                print_step "Installing dependencies via yum..."
                sudo yum install -y curl wget git python3-devel python3-pip
            elif command_exists pacman; then
                print_step "Installing dependencies via pacman..."
                sudo pacman -S --noconfirm curl wget git python python-pip
            else
                print_warning "Package manager not detected. Please install curl, wget, and git manually."
            fi
            ;;
        "windows")
            print_info "On Windows, please ensure you have:"
            print_info "- Git for Windows"
            print_info "- curl (usually included with Windows 10+)"
            ;;
    esac
    
    print_success "System dependencies checked"
}

# Create and setup Python virtual environment
setup_python_env() {
    print_step "Setting up Python virtual environment with uv..."
    
    # Create project with uv
    if [ ! -f "pyproject.toml" ]; then
        print_step "Initializing Python project..."
        uv init --name "$PROJECT_NAME" --python "$PYTHON_VERSION"
    fi
    
    # Create/activate virtual environment
    print_step "Creating virtual environment..."
    uv venv --python "$PYTHON_VERSION"
    
    # Create pyproject.toml with dependencies
    cat > pyproject.toml << EOF
[project]
name = "$PROJECT_NAME"
version = "1.0.0"
description = "Professional stopwatch application for ESP32 Cheap Yellow Display (CYD)"
authors = [
    {name = "CYD Stopwatch", email = "cyd@example.com"}
]
readme = "README.md"
requires-python = ">= $PYTHON_VERSION"
dependencies = [
    "adafruit-ampy>=1.1.0",
    "mpremote>=1.22.0", 
    "esptool>=4.7.0",
    "requests>=2.31.0",
    "rich>=13.7.0",
    "click>=8.1.7",
    "pyserial>=3.5",
    "tqdm>=4.66.0"
]

[project.optional-dependencies]
dev = [
    "pytest>=7.4.0",
    "black>=23.9.0",
    "ruff>=0.1.0",
    "mypy>=1.6.0"
]

[project.urls]
Homepage = "https://github.com/witnessmenow/ESP32-Cheap-Yellow-Display"
Repository = "https://github.com/witnessmenow/ESP32-Cheap-Yellow-Display"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.uv]
dev-dependencies = [
    "pytest>=7.4.0",
    "black>=23.9.0", 
    "ruff>=0.1.0",
    "mypy>=1.6.0"
]
EOF
    
    # Install dependencies
    print_step "Installing Python dependencies..."
    uv sync
    
    print_success "Python environment setup complete"
}

# Download MicroPython libraries
download_micropython_libs() {
    print_step "Downloading MicroPython libraries..."
    
    mkdir -p "$LIB_DIR"
    
    local libraries=(
        "ili9341.py:https://raw.githubusercontent.com/rdagger/micropython-ili9341/master/ili9341.py"
        "xglcd_font.py:https://raw.githubusercontent.com/rdagger/micropython-ili9341/master/xglcd_font.py"
        "xpt2046.py:https://raw.githubusercontent.com/rdagger/micropython-ili9341/master/xpt2046.py"
    )
    
    for lib in "${libraries[@]}"; do
        local filename="${lib%%:*}"
        local url="${lib##*:}"
        local filepath="$LIB_DIR/$filename"
        
        if [ -f "$filepath" ]; then
            print_success "$filename already exists"
        else
            print_step "Downloading $filename..."
            if curl -sL "$url" -o "$filepath"; then
                print_success "Downloaded $filename"
            else
                print_error "Failed to download $filename"
                return 1
            fi
        fi
    done
    
    print_success "MicroPython libraries downloaded"
}

# Create deployment package
create_deployment_package() {
    print_step "Creating deployment package..."
    
    # Clean and create deploy directory
    rm -rf "$DEPLOY_DIR"
    mkdir -p "$DEPLOY_DIR"
    
    # Copy application files
    local app_files=(
        "main.py"
        "stopwatch.py"
        "display_manager.py"
        "touch_handler.py"
        "boot.py"
        "config.py"
    )
    
    for file in "${app_files[@]}"; do
        if [ -f "$file" ]; then
            cp "$file" "$DEPLOY_DIR/"
            print_success "Copied $file"
        else
            print_warning "Missing $file"
        fi
    done
    
    # Copy lib directory
    if [ -d "$LIB_DIR" ]; then
        cp -r "$LIB_DIR" "$DEPLOY_DIR/"
        print_success "Copied lib directory"
    fi
    
    # Create deployment script
    cat > "$DEPLOY_DIR/deploy.sh" << 'EOF'
#!/usr/bin/env bash
# CYD Stopwatch Deployment Script
# This script deploys the application to your CYD device

set -euo pipefail

PORT=""
METHOD="mpremote"

usage() {
    echo "Usage: $0 -p PORT [-m METHOD]"
    echo "  -p PORT    Serial port (e.g., /dev/cu.usbserial-*, /dev/ttyUSB0)"
    echo "  -m METHOD  Deployment method: mpremote, ampy, or thonny (default: mpremote)"
    exit 1
}

while getopts "p:m:h" opt; do
    case $opt in
        p) PORT="$OPTARG" ;;
        m) METHOD="$OPTARG" ;;
        h) usage ;;
        *) usage ;;
    esac
done

if [ -z "$PORT" ]; then
    echo "Error: Port is required"
    usage
fi

echo "Deploying CYD Stopwatch to $PORT using $METHOD..."

case "$METHOD" in
    "mpremote")
        echo "Using mpremote for deployment..."
        mpremote connect "$PORT" fs cp *.py :
        mpremote connect "$PORT" fs mkdir lib
        mpremote connect "$PORT" fs cp lib/* :lib/
        echo "Deployment complete! Reset your CYD to start the application."
        ;;
    "ampy")
        echo "Using ampy for deployment..."
        export AMPY_PORT="$PORT"
        for file in *.py; do
            ampy put "$file" "$file"
        done
        ampy mkdir lib
        for file in lib/*; do
            ampy put "$file" "$file"
        done
        echo "Deployment complete! Reset your CYD to start the application."
        ;;
    *)
        echo "Error: Unsupported method: $METHOD"
        echo "Supported methods: mpremote, ampy"
        exit 1
        ;;
esac
EOF
    
    chmod +x "$DEPLOY_DIR/deploy.sh"
    
    print_success "Deployment package created in $DEPLOY_DIR"
}

# Create helpful scripts
create_helper_scripts() {
    print_step "Creating helper scripts..."
    
    # Development script
    cat > "${PROJECT_DIR}/dev.sh" << EOF
#!/usr/bin/env bash
# CYD Stopwatch Development Helper

set -euo pipefail

cd "\$(dirname "\${BASH_SOURCE[0]}")"

case "\${1:-help}" in
    "test")
        echo "Running tests..."
        uv run python test_stopwatch.py
        ;;
    "demo")
        echo "Running demo..."
        uv run python demo.py
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
    *)
        echo "CYD Stopwatch Development Helper"
        echo "Usage: \$0 {test|demo|format|lint|clean|install|update}"
        echo ""
        echo "Commands:"
        echo "  test    - Run test suite"
        echo "  demo    - Run interactive demo" 
        echo "  format  - Format code with black and ruff"
        echo "  lint    - Run linting with ruff and mypy"
        echo "  clean   - Clean up generated files"
        echo "  install - Install dependencies"
        echo "  update  - Update dependencies"
        ;;
esac
EOF
    
    chmod +x "${PROJECT_DIR}/dev.sh"
    
    # Port finder script
    cat > "${PROJECT_DIR}/find_cyd.sh" << 'EOF'
#!/usr/bin/env bash
# Find CYD device ports

echo "Scanning for CYD devices..."
echo ""

case "$(uname -s)" in
    "Darwin")
        echo "macOS detected - checking USB serial ports:"
        ls /dev/cu.* 2>/dev/null | grep -E "(usbserial|wchusbserial)" || echo "No USB serial devices found"
        ;;
    "Linux")
        echo "Linux detected - checking USB devices:"
        ls /dev/ttyUSB* /dev/ttyACM* 2>/dev/null || echo "No USB devices found"
        ;;
    *)
        echo "Please check Device Manager on Windows for COM ports"
        ;;
esac

echo ""
echo "Common CYD ports:"
echo "  macOS:   /dev/cu.usbserial-*"
echo "  Linux:   /dev/ttyUSB0 or /dev/ttyACM0"
echo "  Windows: COM3, COM4, etc."
EOF
    
    chmod +x "${PROJECT_DIR}/find_cyd.sh"
    
    print_success "Helper scripts created"
}

# Show deployment instructions
show_deployment_instructions() {
    print_header "🚀 DEPLOYMENT INSTRUCTIONS"
    
    echo -e "${GREEN}Your CYD Stopwatch is ready for deployment!${NC}\n"
    
    echo -e "${CYAN}📁 Files prepared in:${NC} ${DEPLOY_DIR}"
    echo -e "${CYAN}🐍 Virtual environment:${NC} ${VENV_DIR}"
    echo ""
    
    echo -e "${YELLOW}STEP 1: Find your CYD device${NC}"
    echo "   ./find_cyd.sh"
    echo ""
    
    echo -e "${YELLOW}STEP 2: Deploy to CYD${NC}"
    echo "   cd deploy"
    echo "   ./deploy.sh -p /dev/cu.usbserial-* -m mpremote"
    echo ""
    
    echo -e "${YELLOW}STEP 3: Alternative deployment methods${NC}"
    echo ""
    echo -e "${BLUE}Using Thonny IDE (Recommended for beginners):${NC}"
    echo "   1. Install Thonny: https://thonny.org/"
    echo "   2. Open Thonny → Tools → Options → Interpreter"
    echo "   3. Select 'MicroPython (ESP32)' and your device port"
    echo "   4. Open each .py file and save to device"
    echo ""
    
    echo -e "${BLUE}Using mpremote (Command line):${NC}"
    echo "   uv run mpremote connect /dev/ttyUSB0 fs cp deploy/*.py :"
    echo "   uv run mpremote connect /dev/ttyUSB0 fs cp deploy/lib/* :lib/"
    echo ""
    
    echo -e "${BLUE}Using ampy (Legacy):${NC}"
    echo "   export AMPY_PORT=/dev/ttyUSB0"
    echo "   uv run ampy put deploy/main.py main.py"
    echo "   # ... repeat for other files"
    echo ""
    
    echo -e "${YELLOW}DEVELOPMENT COMMANDS:${NC}"
    echo "   ./dev.sh test    # Run tests"
    echo "   ./dev.sh demo    # Interactive demo"
    echo "   ./dev.sh format  # Format code"
    echo "   ./dev.sh lint    # Check code quality"
    echo ""
    
    echo -e "${GREEN}🎉 Happy timing with your CYD Stopwatch!${NC}"
}

# Main installation process
main() {
    print_header "🎯 CYD STOPWATCH - UNIVERSAL INSTALLER"
    
    echo "This installer will set up a complete development environment"
    echo "for the CYD Stopwatch application using modern Python tooling."
    echo ""
    
    # Check if we're in the right directory
    if [ ! -f "main.py" ] || [ ! -f "stopwatch.py" ]; then
        print_error "Please run this installer from the plantersensor directory"
        print_error "Expected files: main.py, stopwatch.py, display_manager.py, etc."
        exit 1
    fi
    
    # Installation steps
    install_uv
    install_system_deps
    setup_python_env
    download_micropython_libs
    create_deployment_package
    create_helper_scripts
    
    print_header "✅ INSTALLATION COMPLETE"
    show_deployment_instructions
}

# Handle script interruption
trap 'print_error "Installation interrupted by user"; exit 1' INT TERM

# Run main function
main "$@"
