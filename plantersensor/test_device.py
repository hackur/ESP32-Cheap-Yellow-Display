#!/usr/bin/env python3
"""
CYD Device Tester
=================

This script helps test and verify connection to CYD devices.
It can be used to:
- Test serial communication
- Verify MicroPython installation
- Check device capabilities
- Run basic hardware tests

Usage:
    python test_device.py --port /dev/ttyUSB0
    python test_device.py --scan
"""

import argparse
import sys
import time
import serial
import subprocess
from pathlib import Path
from typing import List, Optional


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
    print(f"\n{Colors.PURPLE}{'=' * 50}{Colors.NC}")
    print(f"{Colors.PURPLE} {text}{Colors.NC}")
    print(f"{Colors.PURPLE}{'=' * 50}{Colors.NC}\n")


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


def scan_ports() -> List[str]:
    """Scan for available serial ports"""
    import glob
    
    ports = []
    
    # Common port patterns
    patterns = [
        '/dev/cu.usbserial-*',  # macOS
        '/dev/cu.wchusbserial-*',  # macOS
        '/dev/ttyUSB*',  # Linux
        '/dev/ttyACM*',  # Linux
    ]
    
    for pattern in patterns:
        ports.extend(glob.glob(pattern))
    
    return sorted(ports)


def test_serial_connection(port: str, baudrate: int = 115200, timeout: float = 2.0) -> bool:
    """Test basic serial connection to a port"""
    try:
        print_step(f"Testing serial connection to {port}...")
        
        with serial.Serial(port, baudrate, timeout=timeout) as ser:
            # Send a simple command
            ser.write(b'\r\n')
            time.sleep(0.1)
            
            # Try to read response
            response = ser.read(100)
            
            if response:
                print_success(f"Serial connection established")
                print(f"   Response: {response.decode('utf-8', errors='ignore').strip()}")
                return True
            else:
                print_warning("No response from device")
                return False
                
    except serial.SerialException as e:
        print_error(f"Serial connection failed: {e}")
        return False
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        return False


def test_micropython_repl(port: str) -> bool:
    """Test MicroPython REPL functionality"""
    try:
        print_step("Testing MicroPython REPL...")
        
        with serial.Serial(port, 115200, timeout=3.0) as ser:
            # Send interrupt to stop any running code
            ser.write(b'\x03')  # Ctrl+C
            time.sleep(0.2)
            
            # Send REPL reset
            ser.write(b'\x04')  # Ctrl+D
            time.sleep(0.5)
            
            # Clear any existing data
            ser.reset_input_buffer()
            
            # Send a simple Python command
            ser.write(b'print("CYD_TEST_OK")\r\n')
            time.sleep(0.5)
            
            # Read response
            response = ser.read(1000).decode('utf-8', errors='ignore')
            
            if "CYD_TEST_OK" in response:
                print_success("MicroPython REPL is working")
                return True
            else:
                print_warning("MicroPython REPL not responding correctly")
                print(f"   Response: {response.strip()}")
                return False
                
    except Exception as e:
        print_error(f"REPL test failed: {e}")
        return False


def test_hardware_info(port: str) -> dict:
    """Get hardware information from the device"""
    try:
        print_step("Getting hardware information...")
        
        commands = [
            "import sys; print('Python:', sys.version)",
            "import gc; print('Free memory:', gc.mem_free())",
            "import machine; print('Frequency:', machine.freq())",
            "try:\n  import esp\n  print('Flash size:', esp.flash_size())\nexcept: pass",
        ]
        
        results = {}
        
        with serial.Serial(port, 115200, timeout=3.0) as ser:
            # Reset REPL
            ser.write(b'\x03\x04')
            time.sleep(0.5)
            ser.reset_input_buffer()
            
            for command in commands:
                ser.write(command.encode() + b'\r\n')
                time.sleep(0.5)
                
                response = ser.read(1000).decode('utf-8', errors='ignore')
                lines = [line.strip() for line in response.split('\n') if line.strip()]
                
                for line in lines:
                    if ':' in line and not line.startswith('>>>'):
                        key, value = line.split(':', 1)
                        results[key.strip()] = value.strip()
        
        if results:
            print_success("Hardware information retrieved:")
            for key, value in results.items():
                print(f"   {key}: {value}")
        else:
            print_warning("Could not retrieve hardware information")
            
        return results
        
    except Exception as e:
        print_error(f"Hardware info test failed: {e}")
        return {}


def test_display_libs(port: str) -> bool:
    """Test if display libraries are available"""
    try:
        print_step("Testing display libraries...")
        
        with serial.Serial(port, 115200, timeout=3.0) as ser:
            # Reset REPL
            ser.write(b'\x03\x04')
            time.sleep(0.5)
            ser.reset_input_buffer()
            
            # Test each library
            libs = ['ili9341', 'xglcd_font', 'xpt2046']
            available_libs = []
            
            for lib in libs:
                ser.write(f'try:\n  import {lib}\n  print("{lib}_OK")\nexcept Exception as e:\n  print("{lib}_ERROR:", e)\n'.encode())
                time.sleep(0.5)
                
                response = ser.read(1000).decode('utf-8', errors='ignore')
                
                if f"{lib}_OK" in response:
                    available_libs.append(lib)
                    print_success(f"Library {lib} is available")
                else:
                    print_warning(f"Library {lib} is missing")
                    if f"{lib}_ERROR" in response:
                        error_line = [line for line in response.split('\n') if f"{lib}_ERROR" in line]
                        if error_line:
                            print(f"   Error: {error_line[0].split(':', 1)[1].strip()}")
            
            return len(available_libs) == len(libs)
            
    except Exception as e:
        print_error(f"Display library test failed: {e}")
        return False


def test_with_mpremote(port: str) -> bool:
    """Test device using mpremote if available"""
    try:
        print_step("Testing with mpremote...")
        
        # Check if mpremote is available
        result = subprocess.run(['which', 'mpremote'], capture_output=True, text=True)
        if result.returncode != 0:
            print_warning("mpremote not found")
            return False
        
        # Test mpremote connection
        cmd = ['mpremote', 'connect', port, 'eval', 'print("MPREMOTE_OK")']
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0 and "MPREMOTE_OK" in result.stdout:
            print_success("mpremote connection successful")
            return True
        else:
            print_warning("mpremote connection failed")
            if result.stderr:
                print(f"   Error: {result.stderr.strip()}")
            return False
            
    except subprocess.TimeoutExpired:
        print_warning("mpremote test timed out")
        return False
    except Exception as e:
        print_error(f"mpremote test failed: {e}")
        return False


def run_comprehensive_test(port: str) -> dict:
    """Run comprehensive device test"""
    print_header(f"COMPREHENSIVE CYD TEST - {port}")
    
    results = {
        'port': port,
        'serial_connection': False,
        'micropython_repl': False,
        'hardware_info': {},
        'display_libs': False,
        'mpremote': False,
        'overall_status': 'FAIL'
    }
    
    # Test serial connection
    results['serial_connection'] = test_serial_connection(port)
    
    if results['serial_connection']:
        # Test MicroPython REPL
        results['micropython_repl'] = test_micropython_repl(port)
        
        if results['micropython_repl']:
            # Get hardware info
            results['hardware_info'] = test_hardware_info(port)
            
            # Test display libraries
            results['display_libs'] = test_display_libs(port)
            
            # Test mpremote
            results['mpremote'] = test_with_mpremote(port)
    
    # Determine overall status
    if results['serial_connection'] and results['micropython_repl']:
        if results['display_libs']:
            results['overall_status'] = 'READY'
        else:
            results['overall_status'] = 'NEEDS_LIBS'
    else:
        results['overall_status'] = 'FAIL'
    
    return results


def print_test_summary(results: dict) -> None:
    """Print test summary"""
    print_header("TEST SUMMARY")
    
    status = results['overall_status']
    port = results['port']
    
    if status == 'READY':
        print_success(f"Device {port} is ready for CYD Stopwatch deployment!")
    elif status == 'NEEDS_LIBS':
        print_warning(f"Device {port} needs display libraries installed")
        print("   Run the installer to download and deploy libraries")
    else:
        print_error(f"Device {port} is not ready")
        print("   Check connection and MicroPython installation")
    
    print(f"\n{Colors.BLUE}Test Results:{Colors.NC}")
    print(f"   Serial Connection: {'✓' if results['serial_connection'] else '✗'}")
    print(f"   MicroPython REPL:  {'✓' if results['micropython_repl'] else '✗'}")
    print(f"   Display Libraries: {'✓' if results['display_libs'] else '✗'}")
    print(f"   mpremote Support:  {'✓' if results['mpremote'] else '✗'}")
    
    if results['hardware_info']:
        print(f"\n{Colors.BLUE}Hardware Info:{Colors.NC}")
        for key, value in results['hardware_info'].items():
            print(f"   {key}: {value}")


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="CYD Device Tester")
    parser.add_argument('--port', '-p', help='Serial port to test (e.g., /dev/ttyUSB0)')
    parser.add_argument('--scan', '-s', action='store_true', help='Scan for available ports')
    parser.add_argument('--test-all', '-a', action='store_true', help='Test all found ports')
    
    args = parser.parse_args()
    
    if args.scan or args.test_all:
        print_step("Scanning for available serial ports...")
        ports = scan_ports()
        
        if not ports:
            print_warning("No serial ports found")
            return
        
        print_success(f"Found {len(ports)} ports:")
        for port in ports:
            print(f"   {port}")
        
        if args.test_all:
            print("\nTesting all ports...")
            for port in ports:
                try:
                    results = run_comprehensive_test(port)
                    print_test_summary(results)
                except KeyboardInterrupt:
                    print_warning("Test interrupted by user")
                    break
                except Exception as e:
                    print_error(f"Test failed for {port}: {e}")
                    
                print()  # Add spacing between tests
    
    elif args.port:
        try:
            results = run_comprehensive_test(args.port)
            print_test_summary(results)
        except KeyboardInterrupt:
            print_warning("Test interrupted by user")
        except Exception as e:
            print_error(f"Test failed: {e}")
    
    else:
        print_error("Please specify --port or --scan")
        parser.print_help()


if __name__ == '__main__':
    main()
