"""
CYD Stopwatch - Test Runner
===========================

Test script to verify the stopwatch logic without hardware dependencies.
This can be run on a desktop environment for testing.
"""

import time
import sys
import os

# Add the current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Mock the machine module for testing
class MockPin:
    OUT = 'OUT'
    def __init__(self, pin, mode=None, value=None):
        self.pin = pin
        self.mode = mode
        self.value = value or 0

    def on(self):
        self.value = 1

    def off(self):
        self.value = 0

    def value(self, val=None):
        if val is not None:
            self.value = val
        return self.value

class MockADC:
    ATTN_11DB = 'ATTN_11DB'
    def __init__(self, pin):
        self.pin = pin

    def atten(self, val):
        pass

    def read(self):
        return 2048  # Mock light sensor reading

class MockSPI:
    def __init__(self, *args, **kwargs):
        pass

# Mock machine module
class MockMachine:
    Pin = MockPin
    ADC = MockADC
    SPI = MockSPI

# Mock time module with MicroPython functions
class MockTime:
    @staticmethod
    def ticks_ms():
        return int(time.time() * 1000)

    @staticmethod
    def ticks_diff(end, start):
        return end - start

    @staticmethod
    def sleep_ms(ms):
        time.sleep(ms / 1000.0)

# Replace modules
sys.modules['machine'] = MockMachine()
original_time = sys.modules['time']
mock_time = MockTime()
# Add our mock functions to the time module
original_time.ticks_ms = mock_time.ticks_ms
original_time.ticks_diff = mock_time.ticks_diff
original_time.sleep_ms = mock_time.sleep_ms

# Now we can import our modules
from stopwatch import Stopwatch

def test_stopwatch():
    """Test the stopwatch functionality"""
    print("Testing Stopwatch...")

    sw = Stopwatch()

    # Test initial state
    assert sw.get_elapsed_time() == 0
    assert not sw.is_running()
    print("✓ Initial state correct")

    # Test start
    sw.start()
    assert sw.is_running()
    print("✓ Start function works")

    # Test timing
    time.sleep(0.1)  # Sleep 100ms
    elapsed = sw.get_elapsed_time()
    assert 80 <= elapsed <= 120  # Allow for some timing variance
    print(f"✓ Timing works: {elapsed}ms")

    # Test stop
    sw.stop()
    assert not sw.is_running()
    stopped_time = sw.get_elapsed_time()
    assert stopped_time >= elapsed
    print(f"✓ Stop function works: {stopped_time}ms")

    # Test resume
    sw.start()
    time.sleep(0.05)  # Sleep 50ms more
    total_time = sw.get_elapsed_time()
    assert total_time >= stopped_time + 40  # At least 40ms more
    print(f"✓ Resume works: {total_time}ms total")

    # Test reset
    sw.reset()
    assert sw.get_elapsed_time() == 0
    assert not sw.is_running()
    print("✓ Reset function works")

    # Test formatting
    sw.start()
    time.sleep(0.1)
    sw.stop()
    formatted = sw.get_formatted_time()
    assert ":" in formatted and "." in formatted
    print(f"✓ Formatting works: {formatted}")

    print("All stopwatch tests passed! ✅")

def test_timing_precision():
    """Test timing precision over longer periods"""
    print("\nTesting timing precision...")

    sw = Stopwatch()
    sw.start()

    # Test multiple start/stop cycles
    for i in range(3):
        time.sleep(0.05)  # 50ms
        sw.stop()
        time.sleep(0.02)  # 20ms pause
        sw.start()

    sw.stop()
    total_time = sw.get_elapsed_time()
    expected_min = 150 - 30  # 3 * 50ms, allow 30ms variance
    expected_max = 150 + 30

    assert expected_min <= total_time <= expected_max
    print(f"✓ Precision test passed: {total_time}ms (expected ~150ms)")

def main():
    """Run all tests"""
    print("=" * 50)
    print("CYD STOPWATCH - TESTING SUITE")
    print("=" * 50)

    try:
        test_stopwatch()
        test_timing_precision()

        print("\n" + "=" * 50)
        print("ALL TESTS PASSED! ✅")
        print("The stopwatch application is ready for deployment.")
        print("=" * 50)

    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
