"""
CYD Planter Sensor - Main Application
====================================

A stopwatch application for the ESP32 Cheap Yellow Display (CYD).
Combines display management, touch handling, and stopwatch functionality
into a complete application.

Features:
- Start/Stop stopwatch with touch controls
- High precision timing with overflow handling
- Modern UI with status indicators
- Light sensor display
- RGB LED status indicators
"""

import time
import gc
from machine import Pin, ADC
from stopwatch import Stopwatch
from display_manager import DisplayManager
from touch_handler import TouchHandler

# Load configuration
try:
    import config
except ImportError:
    # Fallback configuration if config.py not found
    class config:
        DISPLAY_UPDATE_INTERVAL = 100
        TOUCH_DEBOUNCE_MS = 200
        LED_ENABLED = True
        SHOW_MILLISECONDS = True
        SHOW_LIGHT_SENSOR = True
        MEMORY_MANAGEMENT = True
        DEBUG_MODE = False
        STARTUP_DELAY_MS = 100

class StopwatchApp:
    def __init__(self):
        print("Starting CYD Stopwatch Application...")

        # Initialize components
        self.stopwatch = Stopwatch()
        self.display = DisplayManager()
        self.touch = TouchHandler()

        # Initialize RGB LED pins (active low)
        if config.LED_ENABLED:
            self.red_led = Pin(4, Pin.OUT, value=1)    # Off initially
            self.green_led = Pin(16, Pin.OUT, value=1)  # Off initially
            self.blue_led = Pin(17, Pin.OUT, value=1)   # Off initially
        else:
            self.red_led = self.green_led = self.blue_led = None

        # Initialize light sensor
        if config.SHOW_LIGHT_SENSOR:
            self.light_sensor = ADC(Pin(34))
            self.light_sensor.atten(ADC.ATTN_11DB)  # For 0-3.3V range
        else:
            self.light_sensor = None

        # Application state
        self.running = True
        self.last_update = time.ticks_ms()
        self.update_interval = config.DISPLAY_UPDATE_INTERVAL
        self.gc_counter = 0

        # Set initial LED state (blue = ready)
        self.set_led_state('ready')

        print("Application initialized successfully!")

    def set_led_state(self, state):
        """Set RGB LED based on stopwatch state"""
        # Turn off all LEDs first (active low)
        self.red_led.on()
        self.green_led.on()
        self.blue_led.on()

        if state == 'ready':
            self.blue_led.off()  # Blue for ready state
        elif state == 'running':
            self.green_led.off()  # Green for running
        elif state == 'stopped':
            self.red_led.off()   # Red for stopped

    def read_light_level(self):
        """Read light sensor value"""
        try:
            # Take multiple readings for stability
            readings = []
            for _ in range(5):
                readings.append(self.light_sensor.read())
                time.sleep_ms(2)

            # Return average reading
            return sum(readings) // len(readings)
        except:
            return 0

    def handle_touch_input(self):
        """Process touch input and handle button presses"""
        touch_coords = self.touch.get_touch()
        if touch_coords:
            x, y = touch_coords
            print(f"Touch detected at: ({x}, {y})")

            # Check which button was pressed
            if self.display.is_button_touched(x, y, 'start_stop'):
                if self.stopwatch.is_running():
                    self.stopwatch.stop()
                    self.set_led_state('stopped')
                    print("Stopwatch stopped")
                    self.show_statistics()
                else:
                    self.stopwatch.start()
                    self.set_led_state('running')
                    print("Stopwatch started")

            elif self.display.is_button_touched(x, y, 'reset'):
                self.stopwatch.reset()
                self.set_led_state('ready')
                print("Stopwatch reset")

    def update_display(self):
        """Update the display with current stopwatch state"""
        elapsed_time = self.stopwatch.get_elapsed_time()
        is_running = self.stopwatch.is_running()
        light_level = self.read_light_level()

        # Update the display
        self.display.update_stopwatch_display(elapsed_time, is_running, light_level)

    def format_time_string(self, elapsed_ms):
        """Format elapsed time into a readable string"""
        hours = elapsed_ms // 3600000
        minutes = (elapsed_ms % 3600000) // 60000
        seconds = (elapsed_ms % 60000) // 1000
        milliseconds = elapsed_ms % 1000

        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}.{milliseconds:03d}"
        else:
            return f"{minutes:02d}:{seconds:02d}.{milliseconds:03d}"

    def show_statistics(self):
        """Show timing statistics when stopwatch is stopped"""
        if not self.stopwatch.is_running() and self.stopwatch.get_elapsed_time() > 0:
            elapsed = self.stopwatch.get_elapsed_time()

            # Show some basic stats
            total_seconds = elapsed // 1000
            if total_seconds > 0:
                stats_text = f"Total: {self.format_time_string(elapsed)}"
                print(f"Session Statistics: {stats_text}")

    def run_main_loop(self):
        """Main application loop"""
        print("Starting main application loop...")

        try:
            while self.running:
                current_time = time.ticks_ms()

                # Handle touch input
                self.handle_touch_input()

                # Update display at regular intervals
                if time.ticks_diff(current_time, self.last_update) >= self.update_interval:
                    self.update_display()
                    self.last_update = current_time

                    # Periodic garbage collection every 50 updates (~5 seconds)
                    self.gc_counter += 1
                    if self.gc_counter >= 50:
                        gc.collect()
                        self.gc_counter = 0

                # Small delay to prevent excessive CPU usage
                time.sleep_ms(10)

        except KeyboardInterrupt:
            print("\nKeyboard interrupt received. Shutting down...")
            self.running = False
        except Exception as e:
            print(f"Error in main loop: {e}")
            self.display.show_message("ERROR!")
            time.sleep(2)
        finally:
            self.cleanup()

    def cleanup(self):
        """Clean up resources before exit"""
        print("Cleaning up application...")
        try:
            # Turn off all LEDs
            self.red_led.on()
            self.green_led.on()
            self.blue_led.on()

            # Clean up display
            self.display.cleanup()

            # Clean up touch
            self.touch.cleanup()

            print("Cleanup completed.")
        except Exception as e:
            print(f"Error during cleanup: {e}")

# Application entry point
def main():
    """Main application entry point"""
    print("=" * 50)
    print("CYD STOPWATCH APPLICATION")
    print("=" * 50)

    try:
        # Create and run the application
        app = StopwatchApp()
        app.run_main_loop()
    except Exception as e:
        print(f"Fatal error: {e}")
        import sys
        sys.exit(1)

# Auto-run when imported
if __name__ == "__main__":
    main()
else:
    # If imported, still run automatically (MicroPython behavior)
    main()