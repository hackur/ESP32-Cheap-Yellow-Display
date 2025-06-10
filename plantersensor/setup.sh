#!/usr/bin/env bash

# CYD Stopwatch - Universal Installer
# ===================================
#
# This installer sets up a complete development and deployment environment
# for the CYD Stopwatch application using modern Python tooling.
#
# Features:
# - Uses uv for fast Python package management
# - Installs all required command-line tools
# - Downloads MicroPython libraries
# - Creates deployment package
# - Provides deployment instructions
#
# Requirements: macOS, Linux, or Windows with bash/zsh

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

    # Create requirements.txt for dependencies
    cat > requirements.txt << EOF
# Core deployment tools
adafruit-ampy>=1.1.0
mpremote>=1.22.0
esptool>=4.7.0
pyserial>=3.5

# Utility libraries
requests>=2.31.0
rich>=13.7.0
click>=8.1.7
tqdm>=4.66.0
EOF

    # Create dev-requirements.txt for development tools
    cat > dev-requirements.txt << EOF
# Development tools
pytest>=7.4.0
black>=23.9.0
ruff>=0.1.0
mypy>=1.6.0
EOF

    # Create virtual environment
    print_step "Creating virtual environment..."
    uv venv --python "$PYTHON_VERSION"

    # Install core dependencies
    print_step "Installing core dependencies..."
    uv pip install -r requirements.txt

    # Install development dependencies
    print_step "Installing development dependencies..."
    uv pip install -r dev-requirements.txt

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

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

PORT=""
METHOD="mpremote"
VERIFY=false

usage() {
    echo "Usage: $0 -p PORT [-m METHOD] [-v]"
    echo "  -p PORT    Serial port (e.g., /dev/cu.usbserial-*, /dev/ttyUSB0)"
    echo "  -m METHOD  Deployment method: mpremote, ampy, or thonny (default: mpremote)"
    echo "  -v         Verify deployment after upload"
    exit 1
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_step() {
    echo -e "${CYAN}➤ $1${NC}"
}

while getopts "p:m:vh" opt; do
    case $opt in
        p) PORT="$OPTARG" ;;
        m) METHOD="$OPTARG" ;;
        v) VERIFY=true ;;
        h) usage ;;
        *) usage ;;
    esac
done

if [ -z "$PORT" ]; then
    echo "Error: Port is required"
    usage
fi

echo -e "${BLUE}Deploying CYD Stopwatch to $PORT using $METHOD...${NC}"

case "$METHOD" in
    "mpremote")
        print_step "Using mpremote for deployment..."

        # Check if mpremote is available
        if ! command -v mpremote >/dev/null 2>&1; then
            print_error "mpremote not found. Please install it or use the setup script."
            exit 1
        fi

        # Deploy Python files
        print_step "Copying Python files..."
        if mpremote connect "$PORT" fs cp *.py :; then
            print_success "Python files deployed"
        else
            print_error "Failed to deploy Python files"
            exit 1
        fi

        # Create lib directory and deploy libraries
        print_step "Creating lib directory and copying libraries..."
        mpremote connect "$PORT" fs mkdir lib 2>/dev/null || true
        if mpremote connect "$PORT" fs cp lib/* :lib/; then
            print_success "Libraries deployed"
        else
            print_error "Failed to deploy libraries"
            exit 1
        fi

        print_success "Deployment complete!"
        ;;

    "ampy")
        print_step "Using ampy for deployment..."

        # Check if ampy is available
        if ! command -v ampy >/dev/null 2>&1; then
            print_error "ampy not found. Please install it or use the setup script."
            exit 1
        fi

        export AMPY_PORT="$PORT"

        # Deploy Python files
        print_step "Copying Python files..."
        for file in *.py; do
            if [ -f "$file" ]; then
                print_step "Uploading $file..."
                if ampy put "$file" "$file"; then
                    print_success "Uploaded $file"
                else
                    print_error "Failed to upload $file"
                    exit 1
                fi
            fi
        done

        # Create lib directory and deploy libraries
        print_step "Creating lib directory..."
        ampy mkdir lib 2>/dev/null || true

        print_step "Copying libraries..."
        for file in lib/*; do
            if [ -f "$file" ]; then
                filename=$(basename "$file")
                print_step "Uploading lib/$filename..."
                if ampy put "$file" "lib/$filename"; then
                    print_success "Uploaded lib/$filename"
                else
                    print_error "Failed to upload lib/$filename"
                    exit 1
                fi
            fi
        done

        print_success "Deployment complete!"
        ;;

    *)
        print_error "Unsupported method: $METHOD"
        echo "Supported methods: mpremote, ampy"
        exit 1
        ;;
esac

# Verify deployment if requested
if [ "$VERIFY" = true ]; then
    print_step "Verifying deployment..."

    # Check if verification script exists
    if [ -f "../verify_deployment.py" ]; then
        if python3 ../verify_deployment.py --port "$PORT"; then
            print_success "Deployment verification passed!"
        else
            print_error "Deployment verification failed!"
            echo "Some issues were detected. Check the output above for details."
        fi
    else
        echo -e "${YELLOW}⚠ Verification script not found. Skipping verification.${NC}"
    fi
fi

echo ""
echo -e "${GREEN}🎉 CYD Stopwatch deployed successfully!${NC}"
echo ""
echo "Next steps:"
echo "1. Reset your CYD device to start the application"
echo "2. Touch the screen to start/stop the stopwatch"
echo "3. Watch the RGB LED for status indicators:"
echo "   - Blue: Ready to start"
echo "   - Green: Running"
echo "   - Red: Stopped"
echo ""
echo "Troubleshooting:"
echo "- If the screen is blank, check your connections"
echo "- If touch doesn't work, verify the touch pins"
echo "- Run verification: ../dev.sh verify $PORT"
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

# Function to run commands in virtual environment
run_in_venv() {
    if [ -d ".venv" ]; then
        source .venv/bin/activate
        "\$@"
    else
        echo "Error: Virtual environment not found. Run ./setup.sh install first."
        exit 1
    fi
}

case "\${1:-help}" in
    "test")
        echo "Running tests..."
        run_in_venv python test_stopwatch.py
        ;;
    "demo")
        echo "Running demo..."
        run_in_venv python demo.py
        ;;
    "device-test")
        if [ -z "\${2:-}" ]; then
            echo "Testing all devices..."
            run_in_venv python test_device.py --scan --test-all
        else
            echo "Testing device \$2..."
            run_in_venv python test_device.py --port "\$2"
        fi
        ;;
    "verify")
        if [ -z "\${2:-}" ]; then
            echo "Error: Port required for verification"
            echo "Usage: \$0 verify /dev/ttyUSB0"
            exit 1
        else
            echo "Verifying deployment on \$2..."
            run_in_venv python verify_deployment.py --port "\$2"
        fi
        ;;
    "scan")
        echo "Scanning for CYD devices..."
        run_in_venv python test_device.py --scan
        ;;
    "format")
        echo "Formatting code..."
        run_in_venv black *.py
        run_in_venv ruff check --fix *.py
        ;;
    "lint")
        echo "Linting code..."
        run_in_venv ruff check *.py
        run_in_venv mypy *.py --ignore-missing-imports
        ;;
    "clean")
        echo "Cleaning up..."
        rm -rf .venv __pycache__ .pytest_cache .mypy_cache
        rm -rf deploy lib requirements.txt dev-requirements.txt
        ;;
    "install")
        echo "Installing dependencies..."
        if [ -f "requirements.txt" ]; then
            run_in_venv pip install -r requirements.txt
            run_in_venv pip install -r dev-requirements.txt
        else
            echo "Error: requirements.txt not found. Run ./setup.sh install first."
            exit 1
        fi
        ;;
    "update")
        echo "Updating dependencies..."
        if [ -f "requirements.txt" ]; then
            run_in_venv pip install -U -r requirements.txt
            run_in_venv pip install -U -r dev-requirements.txt
        else
            echo "Error: requirements.txt not found. Run ./setup.sh install first."
            exit 1
        fi
        ;;
    "shell")
        echo "Activating development shell..."
        echo "Use 'exit' to leave the shell"
        source .venv/bin/activate && bash
        ;;
    *)
        echo "CYD Stopwatch Development Helper"
        echo "Usage: \$0 {test|demo|device-test|verify|scan|format|lint|clean|install|update|shell}"
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
        echo "  \$0 scan                    # Find CYD devices"
        echo "  \$0 device-test /dev/ttyUSB0    # Test device connection"
        echo "  \$0 verify /dev/ttyUSB0         # Verify deployment"
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

# Detect CYD devices
detect_cyd_devices() {
    print_step "Scanning for CYD devices..."

    local devices=()

    case "$(detect_os)" in
        "macos")
            # Look for USB serial devices
            for port in /dev/cu.usbserial-* /dev/cu.wchusbserial-*; do
                [ -e "$port" ] && devices+=("$port")
            done
            ;;
        "linux")
            # Look for USB devices
            for port in /dev/ttyUSB* /dev/ttyACM*; do
                [ -e "$port" ] && devices+=("$port")
            done
            ;;
        "windows")
            print_info "On Windows, please check Device Manager for COM ports"
            return 0
            ;;
    esac

    if [ ${#devices[@]} -eq 0 ]; then
        print_warning "No potential CYD devices found"
        print_info "Make sure your CYD is connected and drivers are installed"
        return 1
    else
        print_success "Found potential CYD devices:"
        for device in "${devices[@]}"; do
            echo "   $device"
        done
        echo
        return 0
    fi
}

# Interactive deployment
interactive_deploy() {
    print_header "🚀 INTERACTIVE DEPLOYMENT"

    # Check if deployment package exists
    if [ ! -d "$DEPLOY_DIR" ]; then
        print_error "Deployment package not found. Please run setup first."
        return 1
    fi

    # Detect devices
    local detected_devices=()
    if detect_cyd_devices; then
        case "$(detect_os)" in
            "macos")
                for port in /dev/cu.usbserial-* /dev/cu.wchusbserial-*; do
                    [ -e "$port" ] && detected_devices+=("$port")
                done
                ;;
            "linux")
                for port in /dev/ttyUSB* /dev/ttyACM*; do
                    [ -e "$port" ] && detected_devices+=("$port")
                done
                ;;
        esac
    fi

    # Let user select device
    local selected_port=""
    if [ ${#detected_devices[@]} -eq 1 ]; then
        print_info "Found one device: ${detected_devices[0]}"
        read -p "Use this device? (y/n): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            selected_port="${detected_devices[0]}"
        fi
    elif [ ${#detected_devices[@]} -gt 1 ]; then
        echo "Multiple devices detected:"
        for i in "${!detected_devices[@]}"; do
            echo "  $((i+1)). ${detected_devices[i]}"
        done
        echo "  0. Enter manually"

        read -p "Select device (1-${#detected_devices[@]}): " -r choice
        if [[ "$choice" =~ ^[1-9][0-9]*$ ]] && [ "$choice" -le "${#detected_devices[@]}" ]; then
            selected_port="${detected_devices[$((choice-1))]}"
        fi
    fi

    # Manual entry if needed
    if [ -z "$selected_port" ]; then
        read -p "Enter device port manually: " -r selected_port
        if [ -z "$selected_port" ]; then
            print_error "No port specified"
            return 1
        fi
    fi

    # Select deployment method
    echo
    echo "Select deployment method:"
    echo "  1. mpremote (recommended)"
    echo "  2. ampy (legacy)"
    echo "  3. Show manual instructions"

    read -p "Choose method (1-3): " -r method_choice

    case "$method_choice" in
        "1")
            print_step "Deploying with mpremote to $selected_port..."
            if ! command_exists mpremote; then
                print_error "mpremote not found. Installing..."
                uv pip install mpremote
            fi

            cd "$DEPLOY_DIR"

            # Deploy files
            print_step "Copying Python files..."
            if source ../.venv/bin/activate && mpremote connect "$selected_port" fs cp *.py :; then
                print_success "Python files deployed"
            else
                print_error "Failed to deploy Python files"
                return 1
            fi

            # Create lib directory and deploy libraries
            print_step "Creating lib directory and copying libraries..."
            source ../.venv/bin/activate && mpremote connect "$selected_port" fs mkdir lib 2>/dev/null || true
            if source ../.venv/bin/activate && mpremote connect "$selected_port" fs cp lib/* :lib/; then
                print_success "Libraries deployed"
            else
                print_error "Failed to deploy libraries"
                return 1
            fi

            print_success "Deployment complete! Reset your CYD to start the stopwatch."
            ;;

        "2")
            print_step "Deploying with ampy to $selected_port..."
            if ! command_exists ampy; then
                print_error "ampy not found. Installing..."
                uv pip install adafruit-ampy
            fi

            export AMPY_PORT="$selected_port"
            cd "$DEPLOY_DIR"

            # Deploy files
            print_step "Copying Python files..."
            for file in *.py; do
                if [ -f "$file" ]; then
                    print_step "Uploading $file..."
                    if source ../.venv/bin/activate && ampy put "$file" "$file"; then
                        print_success "Uploaded $file"
                    else
                        print_error "Failed to upload $file"
                        return 1
                    fi
                fi
            done

            # Create lib directory and deploy libraries
            print_step "Creating lib directory..."
            source ../.venv/bin/activate && ampy mkdir lib 2>/dev/null || true

            print_step "Copying libraries..."
            for file in lib/*; do
                if [ -f "$file" ]; then
                    local filename=$(basename "$file")
                    print_step "Uploading lib/$filename..."
                    if source ../.venv/bin/activate && ampy put "$file" "lib/$filename"; then
                        print_success "Uploaded lib/$filename"
                    else
                        print_error "Failed to upload lib/$filename"
                        return 1
                    fi
                fi
            done

            print_success "Deployment complete! Reset your CYD to start the stopwatch."
            ;;

        "3")
            show_manual_instructions "$selected_port"
            ;;

        *)
            print_error "Invalid choice"
            return 1
            ;;
    esac
}

# Show manual deployment instructions
show_manual_instructions() {
    local port="${1:-/dev/ttyUSB0}"

    print_header "📖 MANUAL DEPLOYMENT INSTRUCTIONS"

    echo -e "${GREEN}Port: ${port}${NC}"
    echo -e "${GREEN}Files location: ${DEPLOY_DIR}${NC}"
    echo ""

    echo -e "${BLUE}Method 1: Using Thonny IDE (Easiest)${NC}"
    echo "1. Install Thonny: https://thonny.org/"
    echo "2. Open Thonny → Tools → Options → Interpreter"
    echo "3. Select 'MicroPython (ESP32)' and port: $port"
    echo "4. Open each .py file from deploy/ folder"
    echo "5. Save each file to device (Ctrl+Shift+S)"
    echo "6. Create 'lib' folder on device and upload lib files"
    echo ""

    echo -e "${BLUE}Method 2: Using mpremote${NC}"
    echo "uv run mpremote connect $port fs cp $DEPLOY_DIR/*.py :"
    echo "uv run mpremote connect $port fs mkdir lib"
    echo "uv run mpremote connect $port fs cp $DEPLOY_DIR/lib/* :lib/"
    echo ""

    echo -e "${BLUE}Method 3: Using WebREPL (if WiFi configured)${NC}"
    echo "1. Enable WebREPL on your ESP32"
    echo "2. Connect to ESP32 WiFi"
    echo "3. Go to http://micropython.org/webrepl/"
    echo "4. Upload each file manually"
    echo ""
}

# Show deployment instructions
show_deployment_instructions() {
    print_header "🚀 DEPLOYMENT READY"

    echo -e "${GREEN}Your CYD Stopwatch is ready for deployment!${NC}\n"

    echo -e "${CYAN}📁 Files prepared in:${NC} ${DEPLOY_DIR}"
    echo -e "${CYAN}🐍 Virtual environment:${NC} ${VENV_DIR}"
    echo ""

    echo -e "${YELLOW}QUICK DEPLOY OPTIONS:${NC}"
    echo ""
    echo -e "${GREEN}1. Interactive deployment (recommended):${NC}"
    echo "   ./setup.sh deploy"
    echo ""
    echo -e "${GREEN}2. Manual deployment script:${NC}"
    echo "   ./find_cyd.sh                    # Find your device"
    echo "   cd deploy"
    echo "   ./deploy.sh -p /dev/ttyUSB0 -m mpremote"
    echo ""
    echo -e "${GREEN}3. Development commands:${NC}"
    echo "   ./dev.sh test    # Run tests"
    echo "   ./dev.sh demo    # Interactive demo"
    echo "   ./dev.sh format  # Format code"
    echo "   ./dev.sh lint    # Check code quality"
    echo ""

    echo -e "${BLUE}💡 TIP: Run './setup.sh deploy' for guided deployment!${NC}"
    echo ""
    echo -e "${GREEN}🎉 Happy timing with your CYD Stopwatch!${NC}"
}

# Main installation process
main() {
    local command="${1:-install}"

    case "$command" in
        "install"|"setup")
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
            ;;

        "deploy")
            interactive_deploy
            ;;

        "clean")
            print_step "Cleaning up generated files..."
            rm -rf .venv __pycache__ .pytest_cache .mypy_cache
            rm -rf deploy lib pyproject.toml
            rm -f dev.sh find_cyd.sh
            print_success "Cleanup complete"
            ;;

        "update")
            print_step "Updating dependencies..."
            if [ -f "pyproject.toml" ]; then
                uv sync --upgrade
                print_success "Dependencies updated"
            else
                print_error "No pyproject.toml found. Run setup first."
                exit 1
            fi
            ;;

        "status"|"info")
            print_header "📊 PROJECT STATUS"

            echo -e "${CYAN}Project Directory:${NC} $PROJECT_DIR"
            echo -e "${CYAN}Python Version:${NC} $PYTHON_VERSION"
            echo ""

            if [ -d "$VENV_DIR" ]; then
                echo -e "${GREEN}✓ Virtual environment exists${NC}"
            else
                echo -e "${RED}✗ Virtual environment missing${NC}"
            fi

            if [ -f "pyproject.toml" ]; then
                echo -e "${GREEN}✓ Python project configured${NC}"
            else
                echo -e "${RED}✗ Python project not configured${NC}"
            fi

            if [ -d "$LIB_DIR" ]; then
                echo -e "${GREEN}✓ MicroPython libraries downloaded${NC}"
                echo "   $(ls -1 "$LIB_DIR" | wc -l | tr -d ' ') libraries found"
            else
                echo -e "${RED}✗ MicroPython libraries missing${NC}"
            fi

            if [ -d "$DEPLOY_DIR" ]; then
                echo -e "${GREEN}✓ Deployment package ready${NC}"
                echo "   $(ls -1 "$DEPLOY_DIR"/*.py 2>/dev/null | wc -l | tr -d ' ') Python files"
            else
                echo -e "${RED}✗ Deployment package not created${NC}"
            fi

            echo ""
            detect_cyd_devices
            ;;

        "help"|"-h"|"--help")
            print_header "🎯 CYD STOPWATCH INSTALLER HELP"

            echo "Usage: $0 [COMMAND]"
            echo ""
            echo "Commands:"
            echo "  install    - Set up complete development environment (default)"
            echo "  deploy     - Interactive deployment to CYD device"
            echo "  clean      - Remove generated files and virtual environment"
            echo "  update     - Update Python dependencies"
            echo "  status     - Show project status and detected devices"
            echo "  help       - Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0                  # Full setup"
            echo "  $0 install         # Same as above"
            echo "  $0 deploy          # Interactive deployment"
            echo "  $0 status          # Check project status"
            echo ""
            echo "After setup, you can also use:"
            echo "  ./dev.sh test      # Run tests"
            echo "  ./dev.sh demo      # Interactive demo"
            echo "  ./find_cyd.sh      # Find CYD devices"
            ;;

        *)
            print_error "Unknown command: $command"
            print_info "Run '$0 help' for available commands"
            exit 1
            ;;
    esac
}

# Handle script interruption
trap 'print_error "Installation interrupted by user"; exit 1' INT TERM

# Run main function
main "$@"
