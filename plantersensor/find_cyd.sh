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
