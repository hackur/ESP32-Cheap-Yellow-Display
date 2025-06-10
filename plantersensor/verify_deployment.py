#!/usr/bin/env python3
"""
CYD Deployment Verifier
=======================

This script verifies that the CYD Stopwatch application has been
correctly deployed to the device and is functioning properly.

Features:
- Verifies all required files are present
- Tests basic functionality
- Checks hardware components
- Validates configuration

Usage:
    python verify_deployment.py --port /dev/ttyUSB0
"""

import argparse
import sys
import time
import serial
import json
from typing import Dict, List, Optional, Any


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


class CYDVerifier:
    """Main verification class"""
    
    def __init__(self, port: str, baudrate: int = 115200, timeout: float = 3.0):
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.serial = None
        
    def connect(self) -> bool:
        """Connect to the device"""
        try:
            print_step(f"Connecting to device on {self.port}...")
            self.serial = serial.Serial(self.port, self.baudrate, timeout=self.timeout)
            
            # Reset REPL
            self.serial.write(b'\x03\x04')  # Ctrl+C, Ctrl+D
            time.sleep(1.0)
            self.serial.reset_input_buffer()
            
            print_success("Connected to device")
            return True
            
        except Exception as e:
            print_error(f"Connection failed: {e}")
            return False
    
    def disconnect(self) -> None:
        """Disconnect from the device"""
        if self.serial and self.serial.is_open:
            self.serial.close()
    
    def execute_command(self, command: str, wait_time: float = 0.5) -> str:
        """Execute a command and return the response"""
        if not self.serial or not self.serial.is_open:
            raise Exception("Device not connected")
        
        # Clear input buffer
        self.serial.reset_input_buffer()
        
        # Send command
        self.serial.write(command.encode() + b'\r\n')
        time.sleep(wait_time)
        
        # Read response
        response = self.serial.read(2000).decode('utf-8', errors='ignore')
        return response
    
    def check_required_files(self) -> Dict[str, bool]:
        """Check if all required files are present"""
        print_step("Checking required files...")
        
        required_files = [
            'main.py',
            'stopwatch.py',
            'display_manager.py',
            'touch_handler.py',
            'config.py',
            'boot.py',
            'lib/ili9341.py',
            'lib/xglcd_font.py',
            'lib/xpt2046.py'
        ]
        
        results = {}
        
        for file in required_files:
            try:
                command = f"import os; print('{file}' if '{file}' in os.listdir('{file.split('/')[0] if '/' in file else '.'}') else 'MISSING')"
                response = self.execute_command(command)
                
                if file in response and 'MISSING' not in response:
                    results[file] = True
                    print_success(f"Found {file}")
                else:
                    results[file] = False
                    print_error(f"Missing {file}")
                    
            except Exception as e:
                results[file] = False
                print_error(f"Error checking {file}: {e}")
        
        return results
    
    def test_imports(self) -> Dict[str, bool]:
        """Test if all modules can be imported"""
        print_step("Testing module imports...")
        
        modules = [
            'stopwatch',
            'display_manager', 
            'touch_handler',
            'config',
            'ili9341',
            'xglcd_font',
            'xpt2046'
        ]
        
        results = {}
        
        for module in modules:
            try:
                command = f"try:\n  import {module}\n  print('{module}_OK')\nexcept Exception as e:\n  print('{module}_ERROR:', str(e))"
                response = self.execute_command(command, wait_time=1.0)
                
                if f"{module}_OK" in response:
                    results[module] = True
                    print_success(f"Module {module} imported successfully")
                else:
                    results[module] = False
                    error_info = ""
                    if f"{module}_ERROR" in response:
                        lines = response.split('\n')
                        error_lines = [line for line in lines if f"{module}_ERROR" in line]
                        if error_lines:
                            error_info = error_lines[0].split(':', 1)[1].strip()
                    
                    print_error(f"Module {module} failed to import")
                    if error_info:
                        print(f"   Error: {error_info}")
                        
            except Exception as e:
                results[module] = False
                print_error(f"Error testing {module}: {e}")
        
        return results
    
    def test_hardware_components(self) -> Dict[str, bool]:
        """Test hardware components"""
        print_step("Testing hardware components...")
        
        tests = {
            'display': """
try:
    from ili9341 import Display
    from machine import Pin, SPI
    spi = SPI(2, baudrate=40000000, sck=Pin(14), mosi=Pin(13))
    display = Display(spi, dc=Pin(2), cs=Pin(15), rst=Pin(0))
    print('DISPLAY_OK')
except Exception as e:
    print('DISPLAY_ERROR:', str(e))
""",
            'touch': """
try:
    from xpt2046 import Touch
    from machine import Pin, SPI
    spi = SPI(2, baudrate=40000000, sck=Pin(14), mosi=Pin(13))
    touch = Touch(spi, cs=Pin(12), int_pin=Pin(21))
    print('TOUCH_OK')
except Exception as e:
    print('TOUCH_ERROR:', str(e))
""",
            'rgb_led': """
try:
    from machine import Pin, PWM
    red = PWM(Pin(4))
    green = PWM(Pin(16))
    blue = PWM(Pin(17))
    print('RGB_LED_OK')
except Exception as e:
    print('RGB_LED_ERROR:', str(e))
""",
            'light_sensor': """
try:
    from machine import Pin, ADC
    light_sensor = ADC(Pin(34))
    reading = light_sensor.read()
    print('LIGHT_SENSOR_OK:', reading)
except Exception as e:
    print('LIGHT_SENSOR_ERROR:', str(e))
"""
        }
        
        results = {}
        
        for component, test_code in tests.items():
            try:
                response = self.execute_command(test_code, wait_time=2.0)
                
                if f"{component.upper()}_OK" in response:
                    results[component] = True
                    print_success(f"Hardware component {component} is working")
                    
                    # Extract additional info for light sensor
                    if component == 'light_sensor' and 'LIGHT_SENSOR_OK:' in response:
                        lines = response.split('\n')
                        for line in lines:
                            if 'LIGHT_SENSOR_OK:' in line:
                                reading = line.split(':')[1].strip()
                                print(f"   Light sensor reading: {reading}")
                                break
                else:
                    results[component] = False
                    print_error(f"Hardware component {component} failed")
                    
                    # Extract error info
                    error_key = f"{component.upper()}_ERROR"
                    if error_key in response:
                        lines = response.split('\n')
                        error_lines = [line for line in lines if error_key in line]
                        if error_lines:
                            error_info = error_lines[0].split(':', 1)[1].strip()
                            print(f"   Error: {error_info}")
                            
            except Exception as e:
                results[component] = False
                print_error(f"Error testing {component}: {e}")
        
        return results
    
    def test_stopwatch_functionality(self) -> bool:
        """Test basic stopwatch functionality"""
        print_step("Testing stopwatch functionality...")
        
        try:
            # Import and create stopwatch
            test_code = """
try:
    from stopwatch import Stopwatch
    sw = Stopwatch()
    
    # Test basic operations
    sw.start()
    import time
    time.sleep_ms(100)  # Wait 100ms
    elapsed = sw.get_elapsed_time()
    sw.stop()
    
    print('STOPWATCH_OK:', elapsed)
    
    # Test reset
    sw.reset()
    elapsed_after_reset = sw.get_elapsed_time()
    print('RESET_OK:', elapsed_after_reset)
    
except Exception as e:
    print('STOPWATCH_ERROR:', str(e))
"""
            
            response = self.execute_command(test_code, wait_time=2.0)
            
            if 'STOPWATCH_OK:' in response and 'RESET_OK:' in response:
                print_success("Stopwatch functionality is working")
                
                # Extract timing info
                lines = response.split('\n')
                for line in lines:
                    if 'STOPWATCH_OK:' in line:
                        elapsed = line.split(':')[1].strip()
                        print(f"   Elapsed time test: {elapsed}")
                    elif 'RESET_OK:' in line:
                        reset_time = line.split(':')[1].strip()
                        print(f"   Reset test: {reset_time}")
                
                return True
            else:
                print_error("Stopwatch functionality failed")
                if 'STOPWATCH_ERROR:' in response:
                    lines = response.split('\n')
                    error_lines = [line for line in lines if 'STOPWATCH_ERROR:' in line]
                    if error_lines:
                        error_info = error_lines[0].split(':', 1)[1].strip()
                        print(f"   Error: {error_info}")
                return False
                
        except Exception as e:
            print_error(f"Error testing stopwatch: {e}")
            return False
    
    def get_memory_info(self) -> Dict[str, Any]:
        """Get memory and system information"""
        print_step("Getting system information...")
        
        try:
            command = """
import gc, sys
import machine
gc.collect()
print('FREE_MEMORY:', gc.mem_free())
print('TOTAL_MEMORY:', gc.mem_alloc() + gc.mem_free())
print('PYTHON_VERSION:', sys.version)
print('FREQUENCY:', machine.freq())
try:
    import esp
    print('FLASH_SIZE:', esp.flash_size())
except:
    pass
"""
            
            response = self.execute_command(command, wait_time=1.0)
            
            info = {}
            lines = response.split('\n')
            
            for line in lines:
                if ':' in line and any(key in line for key in ['FREE_MEMORY', 'TOTAL_MEMORY', 'PYTHON_VERSION', 'FREQUENCY', 'FLASH_SIZE']):
                    key, value = line.split(':', 1)
                    info[key.strip()] = value.strip()
            
            if info:
                print_success("System information retrieved:")
                for key, value in info.items():
                    formatted_key = key.replace('_', ' ').title()
                    print(f"   {formatted_key}: {value}")
            else:
                print_warning("Could not retrieve system information")
            
            return info
            
        except Exception as e:
            print_error(f"Error getting system info: {e}")
            return {}
    
    def run_comprehensive_verification(self) -> Dict[str, Any]:
        """Run comprehensive verification"""
        print_header("CYD STOPWATCH DEPLOYMENT VERIFICATION")
        
        if not self.connect():
            return {'status': 'CONNECTION_FAILED'}
        
        try:
            results = {
                'status': 'UNKNOWN',
                'files': {},
                'imports': {},
                'hardware': {},
                'stopwatch': False,
                'system_info': {}
            }
            
            # Check files
            results['files'] = self.check_required_files()
            
            # Test imports
            results['imports'] = self.test_imports()
            
            # Test hardware
            results['hardware'] = self.test_hardware_components()
            
            # Test stopwatch functionality
            results['stopwatch'] = self.test_stopwatch_functionality()
            
            # Get system info
            results['system_info'] = self.get_memory_info()
            
            # Determine overall status
            files_ok = all(results['files'].values())
            imports_ok = all(results['imports'].values())
            hardware_ok = len([v for v in results['hardware'].values() if v]) >= 2  # At least 2 components
            
            if files_ok and imports_ok and results['stopwatch'] and hardware_ok:
                results['status'] = 'FULLY_FUNCTIONAL'
            elif files_ok and imports_ok and results['stopwatch']:
                results['status'] = 'BASIC_FUNCTIONAL'
            elif files_ok and imports_ok:
                results['status'] = 'FILES_OK'
            else:
                results['status'] = 'NEEDS_REPAIR'
            
            return results
            
        finally:
            self.disconnect()


def print_verification_summary(results: Dict[str, Any]) -> None:
    """Print verification summary"""
    print_header("VERIFICATION SUMMARY")
    
    status = results['status']
    
    if status == 'CONNECTION_FAILED':
        print_error("Could not connect to device")
        print("   Check that the device is connected and the port is correct")
        return
    
    # Overall status
    if status == 'FULLY_FUNCTIONAL':
        print_success("CYD Stopwatch is fully functional! 🎉")
        print("   All files present, modules working, hardware responsive")
    elif status == 'BASIC_FUNCTIONAL':
        print_warning("CYD Stopwatch is basically functional")
        print("   Core functionality works, but some hardware may need attention")
    elif status == 'FILES_OK':
        print_warning("Files are deployed but functionality is limited")
        print("   Check hardware connections and configuration")
    else:
        print_error("Deployment needs repair")
        print("   Missing files or critical errors detected")
    
    # Detailed results
    print(f"\n{Colors.BLUE}Detailed Results:{Colors.NC}")
    
    # Files
    files_count = len([v for v in results.get('files', {}).values() if v])
    total_files = len(results.get('files', {}))
    print(f"   Files: {files_count}/{total_files} present")
    
    # Imports
    imports_count = len([v for v in results.get('imports', {}).values() if v])
    total_imports = len(results.get('imports', {}))
    print(f"   Imports: {imports_count}/{total_imports} successful")
    
    # Hardware
    hardware_count = len([v for v in results.get('hardware', {}).values() if v])
    total_hardware = len(results.get('hardware', {}))
    print(f"   Hardware: {hardware_count}/{total_hardware} functional")
    
    # Stopwatch
    stopwatch_status = "✓" if results.get('stopwatch', False) else "✗"
    print(f"   Stopwatch: {stopwatch_status}")
    
    # Missing files/modules
    missing_files = [k for k, v in results.get('files', {}).items() if not v]
    if missing_files:
        print(f"\n{Colors.YELLOW}Missing Files:{Colors.NC}")
        for file in missing_files:
            print(f"   {file}")
    
    failed_imports = [k for k, v in results.get('imports', {}).items() if not v]
    if failed_imports:
        print(f"\n{Colors.YELLOW}Failed Imports:{Colors.NC}")
        for module in failed_imports:
            print(f"   {module}")
    
    failed_hardware = [k for k, v in results.get('hardware', {}).items() if not v]
    if failed_hardware:
        print(f"\n{Colors.YELLOW}Non-functional Hardware:{Colors.NC}")
        for component in failed_hardware:
            print(f"   {component}")
    
    # System info
    if results.get('system_info'):
        print(f"\n{Colors.BLUE}System Information:{Colors.NC}")
        for key, value in results['system_info'].items():
            formatted_key = key.replace('_', ' ').title()
            print(f"   {formatted_key}: {value}")


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="CYD Deployment Verifier")
    parser.add_argument('--port', '-p', required=True, help='Serial port (e.g., /dev/ttyUSB0)')
    parser.add_argument('--json', action='store_true', help='Output results as JSON')
    
    args = parser.parse_args()
    
    try:
        verifier = CYDVerifier(args.port)
        results = verifier.run_comprehensive_verification()
        
        if args.json:
            print(json.dumps(results, indent=2))
        else:
            print_verification_summary(results)
            
        # Exit with appropriate code
        if results['status'] in ['FULLY_FUNCTIONAL', 'BASIC_FUNCTIONAL']:
            sys.exit(0)
        else:
            sys.exit(1)
            
    except KeyboardInterrupt:
        print_warning("Verification interrupted by user")
        sys.exit(1)
    except Exception as e:
        print_error(f"Verification failed: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
