"""
Display Manager for CYD Planter Sensor
======================================

Manages the ILI9341 display with modern UI design for the stopwatch application.
Based on the CYD pin configuration and micropython-ili9341 library.
"""

from machine import Pin, SPI
import time
import gc

# Import the ILI9341 display driver and utilities
try:
    from ili9341 import Display, color565
    from xglcd_font import XglcdFont
except ImportError:
    print("Warning: ili9341 libraries not found. Make sure to install them in /lib/")

class DisplayManager:
    def __init__(self):
        print("Initializing display...")

        # CYD Display pin configuration
        self.display_spi = SPI(1, baudrate=80000000, sck=Pin(14), mosi=Pin(13))

        # Initialize display with CYD pins
        # Note: CYD doesn't have a dedicated reset pin, using CS pin
        self.display = Display(
            self.display_spi,
            dc=Pin(2),
            cs=Pin(15),
            rst=Pin(15),
            rotation=0,  # Portrait mode (changed from 1)
            width=320,
            height=240
        )

        # Turn on backlight
        self.backlight = Pin(21, Pin.OUT)
        self.backlight.on()

        # Color definitions
        self.colors = {
            'black': color565(0, 0, 0),
            'white': color565(255, 255, 255),
            'red': color565(255, 0, 0),
            'green': color565(0, 255, 0),
            'blue': color565(0, 0, 255),
            'yellow': color565(255, 255, 0),
            'cyan': color565(0, 255, 255),
            'magenta': color565(255, 0, 255),
            'gray': color565(128, 128, 128),
            'dark_gray': color565(64, 64, 64),
            'light_gray': color565(192, 192, 192)
        }

        # UI Layout constants
        self.screen_width = 320
        self.screen_height = 240

        # Button areas (x, y, width, height)
        self.buttons = {
            'start_stop': (50, 180, 100, 40),
            'reset': (170, 180, 100, 40)
        }

        # Try to load font, fallback to built-in if not available
        try:
            self.large_font = XglcdFont('fonts/Unispace12x24.c', 12, 24)
            self.font_available = True
        except:
            print("Warning: Font file not found. Using built-in display text.")
            self.large_font = None
            self.font_available = False

        # Clear display and show initial screen
        self.display.clear(self.colors['black'])
        self.draw_initial_screen()

        print("Display initialized!")

    def draw_initial_screen(self):
        """Draw the initial application screen"""
        # Clear screen
        self.display.clear(self.colors['black'])

        # Draw title
        title = "CYD STOPWATCH"
        if self.font_available:
            title_x = (self.screen_width - len(title) * 12) // 2
            self.display.draw_text(title_x, 10, title, self.large_font, self.colors['yellow'])
        else:
            # Fallback to simple text - remove font_size parameter
            self.display.draw_text(100, 10, title, self.colors['yellow'])

        # Draw initial time display
        self.draw_time_display("00:00:00.000", False)

        # Draw buttons
        self.draw_buttons("Start", "Reset")

        # Draw status bar
        self.draw_status_bar("Ready", 0)

    def draw_time_display(self, time_str, is_running):
        """Draw the main time display"""
        # Clear time area
        self.display.fill_rect(0, 50, self.screen_width, 80, self.colors['black'])

        # Choose color based on running state
        time_color = self.colors['green'] if is_running else self.colors['white']

        if self.font_available:
            # Calculate center position for time
            time_x = (self.screen_width - len(time_str) * 12) // 2
            self.display.draw_text(time_x, 70, time_str, self.large_font, time_color)
        else:
            # Fallback display - remove font_size parameter
            self.display.draw_text(80, 70, time_str, time_color)

        # Draw running indicator
        if is_running:
            # Blinking dot to indicate running
            current_ms = time.ticks_ms()
            if (current_ms // 500) % 2:  # Blink every 500ms
                self.display.fill_circle(300, 90, 5, self.colors['red'])

    def draw_buttons(self, left_text, right_text):
        """Draw the control buttons"""
        # Start/Stop button
        x, y, w, h = self.buttons['start_stop']
        self.display.fill_rect(x, y, w, h, self.colors['dark_gray'])
        self.display.draw_rect(x, y, w, h, self.colors['white'])

        # Center text in button
        text_x = x + (w - len(left_text) * 8) // 2
        text_y = y + (h - 16) // 2
        self.display.draw_text(text_x, text_y, left_text, color=self.colors['white'])

        # Reset button
        x, y, w, h = self.buttons['reset']
        self.display.fill_rect(x, y, w, h, self.colors['dark_gray'])
        self.display.draw_rect(x, y, w, h, self.colors['white'])

        text_x = x + (w - len(right_text) * 8) // 2
        text_y = y + (h - 16) // 2
        self.display.draw_text(text_x, text_y, right_text, color=self.colors['white'])

    def draw_status_bar(self, status, light_level):
        """Draw status information at the bottom"""
        # Clear status area
        self.display.fill_rect(0, 230, self.screen_width, 10, self.colors['black'])

        # Draw status text
        self.display.draw_text(5, 230, f"Status: {status}", color=self.colors['cyan'])

        # Draw light level indicator
        light_text = f"Light: {light_level//1000}k"
        self.display.draw_text(200, 230, light_text, color=self.colors['cyan'])

    def update_stopwatch_display(self, elapsed_time, is_running, light_level):
        """Update the complete stopwatch display"""
        # Convert elapsed time to formatted string
        hours = elapsed_time // 3600000
        minutes = (elapsed_time % 3600000) // 60000
        seconds = (elapsed_time % 60000) // 1000
        milliseconds = elapsed_time % 1000

        time_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}.{milliseconds:03d}"

        # Update time display
        self.draw_time_display(time_str, is_running)

        # Update button labels based on state
        left_button = "Stop" if is_running else "Start"
        self.draw_buttons(left_button, "Reset")

        # Update status
        if is_running:
            status = "Running"
        elif elapsed_time > 0:
            status = "Stopped"
        else:
            status = "Ready"

        self.draw_status_bar(status, light_level)

    def is_button_touched(self, x, y, button_name):
        """Check if a touch coordinate is within a button area"""
        if button_name not in self.buttons:
            return False

        bx, by, bw, bh = self.buttons[button_name]
        return bx <= x <= bx + bw and by <= y <= by + bh

    def draw_text_centered(self, y, text, color):
        """Draw text centered horizontally"""
        if self.font_available:
            text_width = len(text) * 12
            x = (self.screen_width - text_width) // 2
            self.display.draw_text(x, y, text, self.large_font, color)
        else:
            # Estimate width for built-in font
            text_width = len(text) * 8
            x = (self.screen_width - text_width) // 2
            self.display.draw_text(x, y, text, color=color)

    def show_message(self, message, duration_ms=2000):
        """Show a temporary message on screen"""
        # Save current screen (simplified)
        # Clear center area
        self.display.fill_rect(50, 100, 220, 40, self.colors['black'])
        self.display.draw_rect(50, 100, 220, 40, self.colors['yellow'])

        # Draw message
        self.draw_text_centered(115, message, self.colors['yellow'])

        # Wait and restore (in a real implementation, this would be non-blocking)
        time.sleep_ms(duration_ms)

    def draw_progress_bar(self, x, y, width, height, percentage, color):
        """Draw a progress bar (useful for showing session progress)"""
        # Draw border
        self.display.draw_rect(x, y, width, height, self.colors['white'])

        # Fill progress
        fill_width = int((width - 2) * percentage / 100)
        if fill_width > 0:
            self.display.fill_rect(x + 1, y + 1, fill_width, height - 2, color)

    def display_large_time(self, time_str, is_running):
        """Display time in large, centered format"""
        # Clear the time area
        self.display.fill_rect(20, 60, 280, 60, self.colors['black'])

        # Choose color based on state
        color = self.colors['green'] if is_running else self.colors['cyan']

        # Calculate character width for centering
        char_width = 16 if self.font_available else 12
        text_width = len(time_str) * char_width
        x_pos = (self.screen_width - text_width) // 2

        if self.font_available:
            self.display.draw_text(x_pos, 80, time_str, self.large_font, color)
        else:
            # Fallback to built-in font - remove font_size parameter
            self.display.draw_text(x_pos, 80, time_str, color)

    def cleanup(self):
        """Clean up display resources"""
        try:
            self.display.clear(self.colors['black'])
            self.backlight.off()
        except:
            pass
