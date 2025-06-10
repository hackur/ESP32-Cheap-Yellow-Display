#!/usr/bin/env python3
"""
CYD Stopwatch - Installation Helper
===================================

This script helps you deploy the stopwatch application to your CYD device.
It provides multiple deployment methods and handles library dependencies.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def print_header(title):
    """Print a formatted header"""
    print("\n" + "=" * 60)
    print(f" {title}")
    print("=" * 60)

def print_step(step, description):
    """Print a numbered step"""
    print(f"\n{step}. {description}")

def check_tool_installed(tool_name):
    """Check if a command-line tool is installed"""
    try:
        subprocess.run([tool_name, "--help"],
                      capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def download_libraries():
    """Download required MicroPython libraries"""
    print_step("1", "Downloading required MicroPython libraries...")

    # Create lib directory if it doesn't exist
    lib_dir = Path("lib")
    lib_dir.mkdir(exist_ok=True)

    libraries = [
        ("ili9341.py", "https://raw.githubusercontent.com/rdagger/micropython-ili9341/master/ili9341.py"),
        ("xglcd_font.py", "https://raw.githubusercontent.com/rdagger/micropython-ili9341/master/xglcd_font.py"),
        ("xpt2046.py", "https://raw.githubusercontent.com/rdagger/micropython-ili9341/master/xpt2046.py")
    ]

    # Check if we have curl or wget
    has_curl = check_tool_installed("curl")
    has_wget = check_tool_installed("wget")

    if not has_curl and not has_wget:
        print("❌ Neither curl nor wget is available.")
        print("Please manually download the following files to the 'lib' directory:")
        for filename, url in libraries:
            print(f"   {filename}: {url}")
        return False

    download_tool = "curl" if has_curl else "wget"

    for filename, url in libraries:
        file_path = lib_dir / filename
        if file_path.exists():
            print(f"   ✓ {filename} already exists")
            continue

        print(f"   Downloading {filename}...")
        try:
            if download_tool == "curl":
                subprocess.run(["curl", "-o", str(file_path), url], check=True)
            else:
                subprocess.run(["wget", "-O", str(file_path), url], check=True)
            print(f"   ✓ Downloaded {filename}")
        except subprocess.CalledProcessError:
            print(f"   ❌ Failed to download {filename}")
            return False

    return True

def create_deployment_package():
    """Create a deployment package with all necessary files"""
    print_step("2", "Creating deployment package...")

    # Create deployment directory
    deploy_dir = Path("deploy")
    if deploy_dir.exists():
        shutil.rmtree(deploy_dir)
    deploy_dir.mkdir()

    # Copy application files
    app_files = [
        "main.py",
        "stopwatch.py",
        "display_manager.py",
        "touch_handler.py",
        "boot.py"
    ]

    for file in app_files:
        src = Path(file)
        if src.exists():
            shutil.copy2(src, deploy_dir / file)
            print(f"   ✓ Copied {file}")
        else:
            print(f"   ❌ Missing {file}")
            return False

    # Copy lib directory if it exists
    lib_dir = Path("lib")
    if lib_dir.exists():
        shutil.copytree(lib_dir, deploy_dir / "lib")
        print("   ✓ Copied lib directory")

    print(f"   ✓ Deployment package created in '{deploy_dir}'")
    return True

def show_deployment_instructions():
    """Show manual deployment instructions"""
    print_step("3", "Deployment Instructions")

    print("""
🔧 METHOD 1: Using Thonny IDE (Recommended for beginners)
   1. Install Thonny: https://thonny.org/
   2. Connect your CYD via USB-C cable
   3. In Thonny: Tools → Options → Interpreter
   4. Select "MicroPython (ESP32)" and your device port
   5. Open each .py file and save to device (File → Save as... → MicroPython device)
   6. Reset your CYD - the application will start automatically

🔧 METHOD 2: Using mpremote (Command line)
   1. Install: pip install mpremote
   2. Connect your CYD and run:
      mpremote connect [PORT] fs cp deploy/* :
   3. Reset your device

🔧 METHOD 3: Using ampy (Legacy tool)
   1. Install: pip install adafruit-ampy
   2. Set port: export AMPY_PORT=/dev/ttyUSB0  # (or your device port)
   3. Upload files:
      ampy put deploy/main.py main.py
      ampy put deploy/stopwatch.py stopwatch.py
      ampy put deploy/display_manager.py display_manager.py
      ampy put deploy/touch_handler.py touch_handler.py
      ampy put deploy/boot.py boot.py
      ampy mkdir lib
      ampy put deploy/lib/ili9341.py lib/ili9341.py
      ampy put deploy/lib/xglcd_font.py lib/xglcd_font.py
      ampy put deploy/lib/xpt2046.py lib/xpt2046.py

📱 FINDING YOUR DEVICE PORT:
   • macOS: /dev/cu.usbserial-* or /dev/cu.wchusbserial*
   • Linux: /dev/ttyUSB* or /dev/ttyACM*
   • Windows: COM* (check Device Manager)

🚨 TROUBLESHOOTING:
   • If display is blank: Check if backlight pin is working
   • If touch doesn't work: Verify touch libraries are in /lib
   • If imports fail: Ensure all libraries are properly installed
   • For CYD2USB: Use inverted display settings (see README.md)
""")

def show_usage_instructions():
    """Show how to use the stopwatch application"""
    print_step("4", "How to Use the Stopwatch")

    print("""
🎯 CONTROLS:
   • LEFT BUTTON: Start/Stop the stopwatch
   • RIGHT BUTTON: Reset to 00:00:00.000

📊 DISPLAY:
   • Large time display shows HH:MM:SS.mmm format
   • Status bar shows current state and light level
   • RGB LED on back indicates status:
     - BLUE: Ready/Idle
     - GREEN: Running
     - RED: Stopped

⚡ FEATURES:
   • High precision timing (millisecond accuracy)
   • Handles long timing sessions (hours+)
   • Touch screen interface
   • Ambient light sensor display
   • Modern, easy-to-read UI

🔧 ADVANCED:
   • The stopwatch accumulates time across start/stop cycles
   • Reset clears all accumulated time
   • Application handles timer overflow for very long sessions
   • Memory management prevents crashes during extended use
""")

def main():
    """Main installation process"""
    print_header("CYD STOPWATCH - INSTALLATION HELPER")

    print("This script will help you deploy the stopwatch application to your CYD.")
    print("Make sure your CYD is connected via USB before proceeding.")

    # Check if we're in the right directory
    if not Path("main.py").exists():
        print("\n❌ Error: Run this script from the plantersensor directory")
        print("   Expected files: main.py, stopwatch.py, display_manager.py, etc.")
        sys.exit(1)

    try:
        # Download libraries
        if not download_libraries():
            print("\n⚠️  Library download failed. You'll need to install them manually.")

        # Create deployment package
        if not create_deployment_package():
            print("\n❌ Failed to create deployment package")
            sys.exit(1)

        # Show instructions
        show_deployment_instructions()
        show_usage_instructions()

        print_header("INSTALLATION COMPLETE")
        print("✅ Your stopwatch application is ready to deploy!")
        print("📁 Files are prepared in the 'deploy' directory")
        print("📖 Follow the deployment instructions above")
        print("\n🎉 Happy timing with your CYD Stopwatch!")

    except KeyboardInterrupt:
        print("\n\n⚠️  Installation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Installation failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
