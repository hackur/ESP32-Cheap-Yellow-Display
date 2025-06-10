#!/usr/bin/env python3
"""
MicroPython Firmware Flasher for ESP32 CYD
==========================================

This script downloads and flashes MicroPython firmware to the ESP32 CYD device.
It supports automatic firmware download and flashing with progress indicators.

Usage:
    python flash_micropython.py --port /dev/cu.usbserial-1420
    python flash_micropython.py --port /dev/cu.usbserial-1420 --firmware custom_firmware.bin
"""

import argparse
import os
import sys
import subprocess
import urllib.request
from pathlib import Path
from typing import Optional


class Colors:
    """ANSI color codes for terminal output"""
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    PURPLE = '\033[0;35m'
    CYAN = '\033[0;36m'
    NC = '\033[0m'  # No Color


def print_header(text: str) -> None:
    """Print a formatted header"""
    print(f"\n{Colors.PURPLE}{'=' * 60}{Colors.NC}")
    print(f"{Colors.PURPLE} {text}{Colors.NC}")
    print(f"{Colors.PURPLE}{'=' * 60}{Colors.NC}\n")


def print_step(text: str) -> None:
    """Print a step message"""
    print(f"{Colors.CYAN}➤ {text}{Colors.NC}")


def print_success(text: str) -> None:
    """Print a success message"""
    print(f"{Colors.GREEN}✓ {text}{Colors.NC}")


def print_warning(text: str) -> None:
    """Print a warning message"""
    print(f"{Colors.YELLOW}⚠ {text}{Colors.NC}")


def print_error(text: str) -> None:
    """Print an error message"""
    print(f"{Colors.RED}✗ {text}{Colors.NC}")


def download_firmware(firmware_url: str, output_path: Path) -> bool:
    """Download MicroPython firmware"""
    try:
        print_step(f"Downloading firmware from {firmware_url}")

        def progress_hook(count, block_size, total_size):
            percent = int(count * block_size * 100 / total_size)
            print(f"\r   Progress: {percent}%", end='', flush=True)

        urllib.request.urlretrieve(firmware_url, output_path, progress_hook)
        print()  # New line after progress

        print_success(f"Firmware downloaded to {output_path}")
        return True

    except Exception as e:
        print_error(f"Failed to download firmware: {e}")
        return False


def verify_esptool() -> bool:
    """Verify esptool is available"""
    try:
        result = subprocess.run(['esptool.py', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            version = result.stdout.strip()
            print_success(f"esptool found: {version}")
            return True
        else:
            print_error("esptool not working properly")
            return False
    except FileNotFoundError:
        print_error("esptool.py not found. Please install it with: pip install esptool")
        return False


def erase_flash(port: str) -> bool:
    """Erase the ESP32 flash"""
    try:
        print_step("Erasing ESP32 flash...")

        cmd = ['esptool.py', '--port', port, 'erase_flash']
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0:
            print_success("Flash erased successfully")
            return True
        else:
            print_error(f"Flash erase failed: {result.stderr}")
            return False

    except Exception as e:
        print_error(f"Flash erase failed: {e}")
        return False


def flash_firmware(port: str, firmware_path: Path) -> bool:
    """Flash MicroPython firmware to ESP32"""
    try:
        print_step(f"Flashing firmware: {firmware_path}")

        cmd = [
            'esptool.py',
            '--port', port,
            '--baud', '460800',
            'write_flash',
            '-z',
            '0x1000',
            str(firmware_path)
        ]

        print(f"   Command: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=False, text=True)

        if result.returncode == 0:
            print_success("Firmware flashed successfully!")
            return True
        else:
            print_error("Firmware flashing failed")
            return False

    except Exception as e:
        print_error(f"Firmware flashing failed: {e}")
        return False


def verify_micropython(port: str) -> bool:
    """Verify MicroPython is working after flashing"""
    try:
        print_step("Verifying MicroPython installation...")

        # Wait a moment for the device to reset
        import time
        time.sleep(2)

        # Try to connect with mpremote
        cmd = ['mpremote', 'connect', port, 'eval', 'print("MicroPython OK")']
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)

        if result.returncode == 0 and "MicroPython OK" in result.stdout:
            print_success("MicroPython is working correctly!")
            return True
        else:
            print_warning("MicroPython verification failed, but firmware may still be installed")
            if result.stderr:
                print(f"   Error: {result.stderr.strip()}")
            return False

    except subprocess.TimeoutExpired:
        print_warning("MicroPython verification timed out")
        return False
    except Exception as e:
        print_warning(f"MicroPython verification failed: {e}")
        return False


def get_esp32_firmware_info():
    """Get information about ESP32 firmware options"""
    return {
        'stable': {
            'version': '1.23.0',
            'url': 'https://micropython.org/resources/firmware/ESP32_GENERIC-20240602-v1.23.0.bin',
            'description': 'Latest stable release (recommended)'
        },
        'generic': {
            'version': '1.22.2',
            'url': 'https://micropython.org/resources/firmware/ESP32_GENERIC-20240222-v1.22.2.bin',
            'description': 'Previous stable release'
        }
    }


def select_firmware() -> tuple[str, str]:
    """Let user select firmware version"""
    firmware_info = get_esp32_firmware_info()

    print_header("SELECT MICROPYTHON FIRMWARE")

    print("Available firmware versions:")
    for i, (key, info) in enumerate(firmware_info.items(), 1):
        print(f"   {i}. {info['version']} - {info['description']}")
        print(f"      URL: {info['url']}")
        print()

    while True:
        try:
            choice = input(f"{Colors.CYAN}Select firmware (1-{len(firmware_info)}) [1]: {Colors.NC}").strip()

            if not choice:
                choice = "1"

            choice_idx = int(choice) - 1
            if 0 <= choice_idx < len(firmware_info):
                selected = list(firmware_info.values())[choice_idx]
                return selected['url'], selected['version']
            else:
                print_error("Invalid choice. Please try again.")

        except ValueError:
            print_error("Please enter a number.")
        except KeyboardInterrupt:
            print_error("\nOperation cancelled by user")
            sys.exit(1)


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Flash MicroPython firmware to ESP32 CYD")
    parser.add_argument('--port', '-p', required=True, help='Serial port (e.g., /dev/cu.usbserial-1420)')
    parser.add_argument('--firmware', '-f', help='Custom firmware file path')
    parser.add_argument('--no-verify', action='store_true', help='Skip verification after flashing')
    parser.add_argument('--no-erase', action='store_true', help='Skip flash erase (not recommended)')

    args = parser.parse_args()

    print_header(f"MICROPYTHON FIRMWARE FLASHER")
    print(f"{Colors.BLUE}Target Device: {args.port}{Colors.NC}")

    # Verify tools
    if not verify_esptool():
        sys.exit(1)

    # Determine firmware to use
    if args.firmware:
        firmware_path = Path(args.firmware)
        if not firmware_path.exists():
            print_error(f"Firmware file not found: {firmware_path}")
            sys.exit(1)
        firmware_url = None
        version = "custom"
    else:
        firmware_url, version = select_firmware()
        firmware_path = Path(f"micropython-{version}-esp32.bin")

    print(f"\n{Colors.BLUE}Using firmware: {version}{Colors.NC}")
    if firmware_url:
        print(f"{Colors.BLUE}Source: {firmware_url}{Colors.NC}")
    print(f"{Colors.BLUE}Output: {firmware_path}{Colors.NC}")

    # Confirm before proceeding
    print(f"\n{Colors.YELLOW}⚠ WARNING: This will erase all data on the ESP32!{Colors.NC}")
    confirm = input(f"{Colors.CYAN}Continue? (y/N): {Colors.NC}").strip().lower()

    if confirm not in ['y', 'yes']:
        print_warning("Operation cancelled by user")
        sys.exit(0)

    try:
        # Download firmware if needed
        if firmware_url and not firmware_path.exists():
            if not download_firmware(firmware_url, firmware_path):
                sys.exit(1)

        # Erase flash
        if not args.no_erase:
            if not erase_flash(args.port):
                sys.exit(1)

        # Flash firmware
        if not flash_firmware(args.port, firmware_path):
            sys.exit(1)

        # Verify installation
        if not args.no_verify:
            verify_micropython(args.port)

        print_header("FLASHING COMPLETE")
        print_success("MicroPython firmware has been installed!")
        print()
        print(f"{Colors.CYAN}Next steps:{Colors.NC}")
        print("   1. Test the device: python test_device.py --port " + args.port)
        print("   2. Deploy the stopwatch: ./setup.sh deploy")

    except KeyboardInterrupt:
        print_error("\nOperation interrupted by user")
        sys.exit(1)
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
