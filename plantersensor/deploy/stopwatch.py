"""
Stopwatch Module for CYD Planter Sensor
========================================

Handles timing functionality with proper overflow handling for long duration timing.
Uses time.ticks_ms() with ticks_diff() for accurate timing that handles wraparound.
"""

import time

class Stopwatch:
    def __init__(self):
        self.start_time = 0
        self.total_elapsed = 0
        self.running = False

    def start(self):
        """Start the stopwatch"""
        if not self.running:
            self.start_time = time.ticks_ms()
            self.running = True
            print("Stopwatch started")

    def stop(self):
        """Stop the stopwatch and accumulate elapsed time"""
        if self.running:
            current_time = time.ticks_ms()
            elapsed = time.ticks_diff(current_time, self.start_time)
            self.total_elapsed += elapsed
            self.running = False
            print(f"Stopwatch stopped. Session time: {elapsed}ms")

    def reset(self):
        """Reset the stopwatch to zero"""
        self.start_time = 0
        self.total_elapsed = 0
        self.running = False
        print("Stopwatch reset")

    def get_elapsed_time(self):
        """Get total elapsed time in milliseconds"""
        if self.running:
            current_time = time.ticks_ms()
            current_session = time.ticks_diff(current_time, self.start_time)
            return self.total_elapsed + current_session
        else:
            return self.total_elapsed

    def is_running(self):
        """Check if stopwatch is currently running"""
        return self.running

    def get_formatted_time(self, format_type='full'):
        """Get formatted time string"""
        elapsed = self.get_elapsed_time()

        hours = elapsed // 3600000
        minutes = (elapsed % 3600000) // 60000
        seconds = (elapsed % 60000) // 1000
        milliseconds = elapsed % 1000

        if format_type == 'full':
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}.{milliseconds:03d}"
        elif format_type == 'short':
            if hours > 0:
                return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
            else:
                return f"{minutes:02d}:{seconds:02d}"
        elif format_type == 'minimal':
            if hours > 0:
                return f"{hours}h {minutes}m"
            elif minutes > 0:
                return f"{minutes}m {seconds}s"
            else:
                return f"{seconds}.{milliseconds:03d}s"

        return f"{elapsed}ms"

    def get_session_stats(self):
        """Get statistics about the current timing session"""
        elapsed = self.get_elapsed_time()
        return {
            'total_ms': elapsed,
            'hours': elapsed // 3600000,
            'minutes': (elapsed % 3600000) // 60000,
            'seconds': (elapsed % 60000) // 1000,
            'milliseconds': elapsed % 1000,
            'is_running': self.running,
            'formatted': self.get_formatted_time()
        }

    def lap_time(self):
        """Get current lap time (time since start/resume)"""
        if self.running:
            current_time = time.ticks_ms()
            return time.ticks_diff(current_time, self.start_time)
        return 0

    def get_time_components(self):
        """Get time as separate components for display"""
        total_ms = self.get_elapsed_time()

        hours = total_ms // 3600000
        minutes = (total_ms % 3600000) // 60000
        seconds = (total_ms % 60000) // 1000
        milliseconds = total_ms % 1000

        return {
            'hours': hours,
            'minutes': minutes,
            'seconds': seconds,
            'milliseconds': milliseconds,
            'total_ms': total_ms
        }
