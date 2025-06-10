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
