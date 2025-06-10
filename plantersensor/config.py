# CYD Stopwatch Configuration
# ===========================
#
# This file contains configuration options for the stopwatch application.
# Modify these values to customize the behavior.

# Display Settings
DISPLAY_UPDATE_INTERVAL = 100  # Update interval in milliseconds (10 FPS)
DISPLAY_BRIGHTNESS = 1.0       # Backlight brightness (0.0 to 1.0)

# Touch Settings
TOUCH_DEBOUNCE_MS = 200        # Touch debounce time in milliseconds
TOUCH_STABILITY_MS = 50        # Time to wait for stable touch reading

# LED Settings
LED_BRIGHTNESS = 0.5           # RGB LED brightness (0.0 to 1.0)
LED_ENABLED = True             # Enable/disable RGB LED status indicators

# Timing Settings
TIMER_PRECISION = "high"       # "high" or "standard" precision mode
AUTO_SAVE_ENABLED = False      # Save timing data (requires SD card)

# UI Settings
SHOW_MILLISECONDS = True       # Show milliseconds in time display
SHOW_LIGHT_SENSOR = True       # Display light sensor readings
UI_THEME = "modern"            # "modern", "classic", or "minimal"

# Advanced Settings
MEMORY_MANAGEMENT = True       # Enable automatic garbage collection
DEBUG_MODE = False             # Enable debug output
STARTUP_DELAY_MS = 100         # Delay before starting main loop

# Web Monitor Settings (Optional Feature)
WEB_MONITOR_ENABLED = False    # Enable web-based remote monitoring
WIFI_SSID = ""                 # WiFi network name (set if using web monitor)
WIFI_PASSWORD = ""             # WiFi password (set if using web monitor)
WEB_SERVER_PORT = 80           # Web server port

# Pin Configuration (CYD Standard - don't change unless using different hardware)
PIN_DISPLAY_SCK = 14
PIN_DISPLAY_MOSI = 13
PIN_DISPLAY_DC = 2
PIN_DISPLAY_CS = 15
PIN_DISPLAY_RST = 15
PIN_BACKLIGHT = 21

PIN_TOUCH_SCK = 25
PIN_TOUCH_MOSI = 32
PIN_TOUCH_MISO = 39
PIN_TOUCH_CS = 33
PIN_TOUCH_IRQ = 36

PIN_LED_RED = 4
PIN_LED_GREEN = 16
PIN_LED_BLUE = 17

PIN_LIGHT_SENSOR = 34

# For CYD2USB variant, set this to True
CYD2USB_VARIANT = False
