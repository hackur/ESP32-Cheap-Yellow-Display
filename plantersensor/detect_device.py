#!/usr/bin/env python3
"""
ESP32 CYD Device Detection Script
=================================

This script helps detect and troubleshoot ESP32 CYD connection issues.
"""

import subprocess
import sys
import time
import glob
import os
from pathlib import Path

def run_command(cmd, capture_output=True):
    """Run a command and return the result."""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=capture_output, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def check_usb_devices():
    """Check for USB devices that might be the ESP32."""
    print("🔍 Checking USB devices...")

    # Check for serial devices
    serial_devices = glob.glob("/dev/cu.*") + glob.glob("/dev/tty.*")
    esp_devices = [dev for dev in serial_devices if any(chip in dev.lower() for chip in
                   ['usbserial', 'slab', 'cp210', 'ch340', 'ch341', 'ftdi', 'esp'])]

    if esp_devices:
        print(f"✅ Found potential ESP32 devices: {esp_devices}")
        return esp_devices
    else:
        print("❌ No ESP32-like devices found")
        print(f"📋 All serial devices: {serial_devices}")
        return []

def check_system_usb():
    """Check system USB information."""
    print("\n🔍 Checking system USB information...")

    success, output, error = run_command("system_profiler SPUSBDataType")
    if success:
        # Look for ESP32-related keywords
        lines = output.lower().split('\n')
        esp_lines = [line for line in lines if any(keyword in line for keyword in
                    ['esp', 'serial', 'ch340', 'cp210', 'ftdi', 'uart', 'silicon labs'])]

        if esp_lines:
            print("✅ Found USB devices that might be ESP32:")
            for line in esp_lines:
                print(f"   {line.strip()}")
        else:
            print("❌ No ESP32-related USB devices found in system")
    else:
        print(f"❌ Error checking USB devices: {error}")

def check_drivers():
    """Check if necessary drivers are installed."""
    print("\n🔍 Checking for USB-to-Serial drivers...")

    # Check for common driver files
    driver_paths = [
        "/System/Library/Extensions/SiLabsUSBDriver.kext",
        "/Library/Extensions/SiLabsUSBDriver.kext",
        "/System/Library/Extensions/FTDIUSBSerialDriver.kext",
        "/Library/Extensions/FTDIUSBSerialDriver.kext"
    ]

    found_drivers = []
    for path in driver_paths:
        if os.path.exists(path):
            found_drivers.append(path)

    if found_drivers:
        print("✅ Found USB-to-Serial drivers:")
        for driver in found_drivers:
            print(f"   {driver}")
    else:
        print("❌ No common USB-to-Serial drivers found")

def check_esptool():
    """Check if esptool is available and can detect devices."""
    print("\n🔍 Checking esptool...")

    # Try different esptool commands
    esptool_commands = ['esptool.py', 'esptool', 'python -m esptool']

    for cmd in esptool_commands:
        success, output, error = run_command(f"{cmd} version")
        if success:
            print(f"✅ Found working esptool: {cmd}")
            print(f"   Version: {output.strip()}")

            # Try to list ports
            print("   Checking for ESP32 devices...")
            success, output, error = run_command(f"{cmd} --list-ports")
            if success and output.strip():
                print(f"   📋 Available ports: {output.strip()}")
            else:
                print("   ❌ No ports detected by esptool")
            return True

    print("❌ esptool not found or not working")
    return False

def provide_troubleshooting():
    """Provide troubleshooting steps."""
    print("\n" + "="*60)
    print("🛠️  TROUBLESHOOTING GUIDE")
    print("="*60)

    print("\n1. 🔌 CONNECTION CHECKLIST:")
    print("   • Use a MICRO USB cable (not USB-C)")
    print("   • Ensure the cable supports DATA (not just charging)")
    print("   • Try a different USB cable")
    print("   • Try a different USB port")
    print("   • Make sure the ESP32 is powered on")

    print("\n2. 🎛️  ESP32 MODE:")
    print("   • Try holding the BOOT button while connecting")
    print("   • Press and release the EN/RST button")
    print("   • Some ESP32s need to be in download mode")

    print("\n3. 💾 DRIVER INSTALLATION:")
    print("   • For CH340/CH341 chips:")
    print("     Download from: https://github.com/WCHSoftGroup/ch34xser_macos")
    print("   • For CP210x chips:")
    print("     Download from: https://www.silabs.com/developers/usb-to-uart-bridge-vcp-drivers")
    print("   • For FTDI chips:")
    print("     Download from: https://ftdichip.com/drivers/vcp-drivers/")

    print("\n4. 🔄 SYSTEM STEPS:")
    print("   • After driver installation, restart your computer")
    print("   • Check System Preferences > Security & Privacy")
    print("   • Allow any blocked drivers")
    print("   • Unplug and replug the device")

    print("\n5. 🧪 TESTING:")
    print("   • After following steps, run this script again")
    print("   • Try: ls -la /dev/cu.* | grep -i usb")
    print("   • Try: esptool.py --list-ports")

def main():
    """Main detection function."""
    print("ESP32 CYD Device Detection")
    print("=" * 30)

    # Check for devices
    devices = check_usb_devices()

    # Check system USB
    check_system_usb()

    # Check drivers
    check_drivers()

    # Check esptool
    esptool_available = check_esptool()

    # Summary
    print("\n" + "="*60)
    print("📊 DETECTION SUMMARY")
    print("="*60)

    if devices:
        print(f"✅ Serial devices found: {len(devices)}")
        for device in devices:
            print(f"   📍 {device}")
    else:
        print("❌ No ESP32 devices detected")

    if esptool_available:
        print("✅ esptool is available")
    else:
        print("❌ esptool issues detected")

    if not devices:
        provide_troubleshooting()
    else:
        print("\n🎉 Device(s) found! You can proceed with flashing.")
        print("   Next step: ./setup.sh flash-firmware")

if __name__ == "__main__":
    main()
