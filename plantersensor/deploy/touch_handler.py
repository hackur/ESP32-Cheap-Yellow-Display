"""
Touch Handler for CYD Planter Sensor
====================================

Manages XPT2046 touch screen input for the CYD display.
Based on the CYD pin configuration and touch examples.
"""

from machine import Pin, SPI
import time

# Import touch driver
try:
    from xpt2046 import Touch
except ImportError:
    print("Warning: xpt2046 library not found. Make sure to install it in /lib/")

class TouchHandler:
    def __init__(self):
        print("Initializing touch handler...")

        # CYD Touch pin configuration
        # Touch screen uses different SPI pins than display
        self.touch_spi = SPI(1, baudrate=1000000, sck=Pin(25), mosi=Pin(32), miso=Pin(39))

        # Initialize touch handler
        try:
            self.touch = Touch(
                self.touch_spi,
                cs=Pin(33),
                int_pin=Pin(36),
                int_handler=self._touch_interrupt
            )
            self.touch_available = True
        except:
            print("Warning: Touch initialization failed. Touch input will not work.")
            self.touch = None
            self.touch_available = False

        # Touch state tracking
        self.last_touch_time = 0
        self.touch_debounce = 200  # 200ms debounce
        self.last_touch_pos = None

        print("Touch handler initialized!")

    def _touch_interrupt(self, x, y):
        """Internal touch interrupt handler"""
        current_time = time.ticks_ms()

        # Simple debounce
        if time.ticks_diff(current_time, self.last_touch_time) > self.touch_debounce:
            self.last_touch_pos = (x, y)
            self.last_touch_time = current_time
            print(f"Touch interrupt: ({x}, {y})")

    def get_touch(self):
        """Get touch coordinates if available"""
        if not self.touch_available:
            return None

        try:
            # Check for touch and return coordinates
            touch_data = self.touch.get_touch()
            if touch_data:
                return touch_data

            # Also check if we have a recent interrupt-based touch
            if self.last_touch_pos:
                pos = self.last_touch_pos
                self.last_touch_pos = None  # Clear after reading
                return pos

        except Exception as e:
            print(f"Touch read error: {e}")

        return None

    def is_touched(self):
        """Check if screen is currently being touched"""
        if not self.touch_available:
            return False

        try:
            return self.touch.get_touch() is not None
        except:
            return False

    def wait_for_touch(self, timeout_ms=5000):
        """Wait for a touch input with timeout"""
        if not self.touch_available:
            return None

        start_time = time.ticks_ms()

        while time.ticks_diff(time.ticks_ms(), start_time) < timeout_ms:
            touch = self.get_touch()
            if touch:
                return touch
            time.sleep_ms(10)

        return None

    def calibrate_touch(self):
        """Simple touch calibration (if needed)"""
        # This would implement touch calibration
        # For now, we assume the touch is properly calibrated
        print("Touch calibration not implemented - using default calibration")
        return True

    def get_stable_touch(self, stability_time=50):
        """Get a stable touch reading by requiring consistent position"""
        first_touch = self.get_touch()
        if not first_touch:
            return None

        # Wait for stability
        time.sleep_ms(stability_time)

        # Verify touch is still in similar position
        second_touch = self.get_touch()
        if second_touch:
            x1, y1 = first_touch
            x2, y2 = second_touch

            # Check if touches are close enough (within 20 pixels)
            if abs(x1 - x2) < 20 and abs(y1 - y2) < 20:
                return ((x1 + x2) // 2, (y1 + y2) // 2)  # Return average

        return None

    def test_touch_calibration(self):
        """Simple touch calibration test"""
        print("Touch calibration test - touch all corners of screen")
        corners_touched = 0
        test_timeout = 30000  # 30 seconds
        start_time = time.ticks_ms()

        while corners_touched < 4 and time.ticks_diff(time.ticks_ms(), start_time) < test_timeout:
            touch = self.get_touch()
            if touch:
                x, y = touch
                print(f"Touch at: ({x}, {y})")
                corners_touched += 1
                time.sleep_ms(1000)  # Wait 1 second between touches

        return corners_touched >= 4

    def cleanup(self):
        """Clean up touch resources"""
        try:
            if self.touch_available and self.touch:
                # Touch cleanup if needed
                pass
        except:
            pass
