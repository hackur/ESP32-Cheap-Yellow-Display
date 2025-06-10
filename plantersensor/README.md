# CYD Planter Sensor - Stopwatch Application

A professional stopwatch application for the ESP32 Cheap Yellow Display (CYD) board, implemented in MicroPython with advanced features and modern UI design.

## ✨ Features

### Core Functionality
- **⏱️ High-Precision Timing**: Millisecond accuracy with overflow handling
- **🎯 Touch Controls**: Intuitive start/stop and reset buttons
- **📱 Modern UI**: Clean, responsive interface optimized for the CYD display
- **💾 Session Management**: Accumulates time across multiple start/stop cycles

### Visual Feedback
- **🌈 RGB LED Status**: Color-coded status indicators
  - 🔵 Blue: Ready/Idle state
  - 🟢 Green: Timing in progress
  - 🔴 Red: Timer stopped/paused
- **📊 Live Display**: Real-time time updates with status information
- **💡 Light Sensor**: Ambient light level monitoring and display

### Advanced Features
- **⚙️ Configurable Settings**: Customizable via `config.py`
- **🧠 Memory Management**: Automatic garbage collection for long sessions
- **🔧 Error Handling**: Robust error recovery and graceful degradation
- **📐 Multiple Time Formats**: Full, short, and minimal display options
- **🌐 Web Monitor** (Optional): Remote monitoring via WiFi
- **🧪 Test Suite**: Comprehensive testing framework included

## 📁 Project Structure

```
plantersensor/
├── main.py              # Main application entry point
├── stopwatch.py         # Core timing logic
├── display_manager.py   # Display and UI management
├── touch_handler.py     # Touch screen input handling
├── config.py            # Configuration settings
├── boot.py              # Boot-time initialization
├── web_monitor.py       # Optional web interface
├── test_stopwatch.py    # Test suite
├── demo.py              # Interactive demonstration
├── install.py           # Installation helper script
├── README.md            # This file
└── lib/                 # Required MicroPython libraries
    ├── ili9341.py
    ├── xglcd_font.py
    └── xpt2046.py
```

## 🚀 Quick Start

### Option 1: Automated Setup (Recommended)

The easiest way to get started is using our interactive installer:

```bash
# Navigate to the project directory
cd /path/to/ESP32-Cheap-Yellow-Display/plantersensor

# Run the universal installer
./setup.sh

# Deploy interactively (detects your CYD automatically)
./setup.sh deploy
```

### Option 2: Manual Setup

If you prefer manual control or want to understand the process:

```bash
# Install dependencies manually
pip install adafruit-ampy mpremote esptool pyserial requests

# Download MicroPython libraries
python install.py

# Deploy to your CYD
mpremote connect /dev/ttyUSB0 fs cp *.py :
mpremote connect /dev/ttyUSB0 fs cp lib/* :lib/
```

## 🛠️ Development Tools

### Universal Installer (`setup.sh`)

The setup script provides a complete development environment:

```bash
./setup.sh install    # Full setup (default)
./setup.sh deploy     # Interactive deployment
./setup.sh status     # Check project status
./setup.sh clean      # Clean up generated files
./setup.sh help       # Show all commands
```

### Development Helper (`dev.sh`)

Once set up, use the development helper for daily workflows:

```bash
./dev.sh scan                      # Find CYD devices
./dev.sh device-test /dev/ttyUSB0   # Test device connection
./dev.sh verify /dev/ttyUSB0        # Verify deployment
./dev.sh test                       # Run test suite
./dev.sh demo                       # Interactive demo
./dev.sh format                     # Format code
./dev.sh lint                       # Check code quality
```

### Device Management

#### Find Your CYD Device
```bash
./find_cyd.sh                       # Auto-detect CYD ports
./dev.sh scan                       # Scan with detailed info
```

#### Test Device Connection
```bash
./dev.sh device-test /dev/ttyUSB0   # Test specific device
./dev.sh device-test                # Test all found devices
```

#### Verify Deployment
```bash
./dev.sh verify /dev/ttyUSB0        # Comprehensive verification
```

## 📦 Deployment Options

### Interactive Deployment (Recommended)
```bash
./setup.sh deploy
```
- Automatically detects connected CYD devices
- Guides you through deployment method selection
- Provides real-time feedback and error handling
- Includes optional verification step

### Manual Deployment Scripts

#### Using the Deploy Script
```bash
cd deploy
./deploy.sh -p /dev/ttyUSB0 -m mpremote -v
```

#### Direct mpremote
```bash
source .venv/bin/activate
mpremote connect /dev/ttyUSB0 fs cp deploy/*.py :
mpremote connect /dev/ttyUSB0 fs cp deploy/lib/* :lib/
```

#### Direct ampy
```bash
source .venv/bin/activate
export AMPY_PORT=/dev/ttyUSB0
for file in deploy/*.py; do ampy put "$file" "$(basename "$file")"; done
ampy mkdir lib
for file in deploy/lib/*; do ampy put "$file" "lib/$(basename "$file")"; done
```

## 🧪 Testing & Quality Assurance

### Automated Testing
```bash
./dev.sh test                       # Run full test suite
python test_stopwatch.py            # Direct test execution
```

### Interactive Demo
```bash
./dev.sh demo                       # Feature demonstration
python demo.py                      # Direct demo execution
```

### Code Quality
```bash
./dev.sh format                     # Auto-format with black & ruff
./dev.sh lint                       # Check with ruff & mypy
```

### Device Verification
```bash
./dev.sh verify /dev/ttyUSB0        # Comprehensive device check
python verify_deployment.py -p /dev/ttyUSB0 --json  # JSON output
```

## Hardware Requirements

- ESP32 Cheap Yellow Display (CYD) board
- The CYD should have:
  - ILI9341 320x240 TFT display
  - XPT2046 touch controller
  - RGB LED
  - Light sensor (LDR)
  - USB-C connector for power and programming

## Software Requirements

### MicroPython Firmware
1. Install the latest MicroPython firmware for ESP32:
   ```bash
   # Download from https://micropython.org/download/ESP32_GENERIC/
   # Flash using esptool:
   esptool.py --chip esp32 --port /dev/ttyUSB0 erase_flash
   esptool.py --chip esp32 --port /dev/ttyUSB0 write_flash -z 0x1000 ESP32_GENERIC-20240602-v1.23.0.bin
   ```

### Required Libraries
The application requires the following MicroPython libraries to be installed in the `/lib` directory on your CYD:

1. **ili9341.py** - Display driver
2. **xglcd_font.py** - Font support
3. **xpt2046.py** - Touch screen driver

You can get these from:
- [micropython-ili9341](https://github.com/rdagger/micropython-ili9341)
- Download the files and copy them to the `/lib` folder on your CYD

### Optional Font Files
For better text rendering, copy font files to `/fonts` directory:
- **Unispace12x24.c** - Font file (from micropython-ili9341 repository)

## Installation and Deployment

### Method 1: Using Thonny IDE (Recommended)

1. **Install Thonny IDE**:
   ```bash
   # On macOS with Homebrew:
   brew install --cask thonny

   # Or download from: https://thonny.org/
   ```

2. **Connect your CYD**:
   - Connect the CYD via USB-C cable
   - The board should appear as a serial device (usually `/dev/ttyUSB0` on Linux or `/dev/cu.usbserial-*` on macOS)

3. **Configure Thonny**:
   - Open Thonny
   - Go to Tools → Options → Interpreter
   - Select "MicroPython (ESP32)"
   - Choose the correct port

4. **Install Required Libraries**:
   - In Thonny, go to Tools → Manage packages
   - Search for and install the required libraries, or manually copy them to `/lib`

5. **Deploy the Application**:
   - Open each Python file from the `plantersensor` directory in Thonny
   - Save each file to the CYD device:
     - `main.py` → save to device root
     - `stopwatch.py` → save to device root
     - `display_manager.py` → save to device root
     - `touch_handler.py` → save to device root

6. **Run the Application**:
   - In Thonny, with `main.py` open, click "Run current script" (F5)
   - Or reset the CYD board - it will automatically run `main.py`

### Method 2: Using ampy (Command Line)

1. **Install ampy**:
   ```bash
   pip install adafruit-ampy
   ```

2. **Deploy files**:
   ```bash
   # Set your CYD's serial port
   export AMPY_PORT=/dev/ttyUSB0  # Linux
   # export AMPY_PORT=/dev/cu.usbserial-*  # macOS

   # Copy application files
   ampy put plantersensor/main.py main.py
   ampy put plantersensor/stopwatch.py stopwatch.py
   ampy put plantersensor/display_manager.py display_manager.py
   ampy put plantersensor/touch_handler.py touch_handler.py

   # Create lib directory and copy libraries
   ampy mkdir lib
   ampy put path/to/ili9341.py lib/ili9341.py
   ampy put path/to/xglcd_font.py lib/xglcd_font.py
   ampy put path/to/xpt2046.py lib/xpt2046.py

   # Optional: Copy fonts
   ampy mkdir fonts
   ampy put path/to/Unispace12x24.c fonts/Unispace12x24.c
   ```

3. **Reset the CYD** to start the application

### Method 3: Using mpremote (Modern Tool)

1. **Install mpremote**:
   ```bash
   pip install mpremote
   ```

2. **Deploy and run**:
   ```bash
   # Connect and copy files
   mpremote connect /dev/ttyUSB0 fs cp plantersensor/main.py :main.py
   mpremote connect /dev/ttyUSB0 fs cp plantersensor/stopwatch.py :stopwatch.py
   mpremote connect /dev/ttyUSB0 fs cp plantersensor/display_manager.py :display_manager.py
   mpremote connect /dev/ttyUSB0 fs cp plantersensor/touch_handler.py :touch_handler.py

   # Run the application
   mpremote connect /dev/ttyUSB0 exec "import main"
   ```

## Usage

1. **Power On**: Connect the CYD via USB-C. The application will start automatically.

2. **Interface**:
   - Large time display in center showing HH:MM:SS.mmm
   - Two buttons at bottom:
     - Left button: Start/Stop
     - Right button: Reset
   - Status bar showing current state and light level
   - RGB LED on back indicating status

3. **Controls**:
   - Tap "Start" to begin timing
   - Tap "Stop" to pause (time accumulates)
   - Tap "Reset" to clear all time and return to 00:00:00.000
   - The stopwatch can run for extended periods (handles timer wraparound properly)

## Troubleshooting

### Display Issues
- **Black screen**: Check if backlight is working, verify power supply
- **Flickering**: Try different USB cable/power supply
- **No display**: Verify MicroPython firmware is installed correctly

### Touch Not Working
- **No touch response**: Check if touch libraries are installed in `/lib`
- **Inaccurate touch**: May need calibration (not implemented in basic version)

### Application Crashes
- **Import errors**: Ensure all required libraries are in `/lib` directory
- **Memory errors**: The application includes garbage collection, but very long runtimes might need a reset

### Library Installation
If you get import errors:
1. Download the required libraries from the GitHub repositories mentioned above
2. Copy them to the `/lib` directory on your CYD
3. Restart the application

## Development Notes

- The application uses `time.ticks_ms()` and `ticks_diff()` for precise timing that handles timer wraparound
- Touch debouncing is implemented to prevent false triggers
- The display updates at 10 FPS (100ms intervals) for smooth operation
- Memory management includes periodic garbage collection
- All pin definitions match the standard CYD configuration

## Pin Configuration (CYD Standard)

- **Display**: SPI1, SCK=14, MOSI=13, DC=2, CS=15, RST=15
- **Touch**: SPI1, SCK=25, MOSI=32, MISO=39, CS=33, INT=36
- **Backlight**: Pin 21
- **RGB LED**: Red=4, Green=16, Blue=17 (active low)
- **Light Sensor**: ADC Pin 34

## Future Enhancements

- WiFi connectivity for time synchronization
- Data logging to SD card
- Multiple timer modes
- Touch calibration
- Custom themes
- Sensor data logging (temperature, humidity, etc.)

For issues or contributions, please refer to the main CYD project repository.


# Cool Stuff

```
(plantersensor) ➜  plantersensor git:(micropython-playground) ✗ cd /Users/sarda/Projects/arduino/ESP32-Cheap-Yellow-Display/plantersensor && source .venv/bin/activate && esptool.py --port /dev/cu.usbserial-1420 flash_id
esptool.py v4.8.1
Serial port /dev/cu.usbserial-1420
Connecting.....
Detecting chip type... Unsupported detection protocol, switching and trying again...
Connecting.....
Detecting chip type... ESP32
Chip is ESP32-D0WD-V3 (revision v3.1)
Features: WiFi, BT, Dual Core, 240MHz, VRef calibration in efuse, Coding Scheme None
Crystal is 40MHz
MAC: d0:ef:76:57:90:50
Uploading stub...
Running stub...
Stub running...
Manufacturer: 85
Device: 2016
Detected flash size: 4MB
Flash voltage set by a strapping pin to 3.3V
Hard resetting via RTS pin...
```