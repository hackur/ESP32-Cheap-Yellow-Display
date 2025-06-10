"""
CYD Stopwatch - Demo Script
===========================

This script demonstrates the stopwatch functionality without requiring
the full hardware setup. Useful for testing and demonstration.
"""

import time
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the test mocks
from test_stopwatch import MockMachine, MockTime

# Setup mocks
sys.modules['machine'] = MockMachine()
original_time = sys.modules['time']
mock_time = MockTime()
original_time.ticks_ms = mock_time.ticks_ms
original_time.ticks_diff = mock_time.ticks_diff
original_time.sleep_ms = mock_time.sleep_ms

# Now import our stopwatch
from stopwatch import Stopwatch

def demo_basic_timing():
    """Demonstrate basic timing functionality"""
    print("\n🎯 BASIC TIMING DEMO")
    print("-" * 30)

    sw = Stopwatch()

    # Start timing
    print("Starting stopwatch...")
    sw.start()

    # Simulate some work
    for i in range(3):
        time.sleep(0.5)
        elapsed = sw.get_elapsed_time()
        formatted = sw.get_formatted_time()
        print(f"  {i+1}. Running: {formatted} ({elapsed}ms)")

    # Stop timing
    sw.stop()
    final_time = sw.get_formatted_time()
    print(f"✅ Final time: {final_time}")

def demo_start_stop_cycles():
    """Demonstrate start/stop cycles"""
    print("\n⏯️ START/STOP CYCLES DEMO")
    print("-" * 30)

    sw = Stopwatch()

    for cycle in range(3):
        print(f"\nCycle {cycle + 1}:")

        # Start
        sw.start()
        print(f"  ▶️  Started")

        # Run for random time
        run_time = 0.3 + (cycle * 0.2)
        time.sleep(run_time)

        # Stop
        sw.stop()
        elapsed = sw.get_formatted_time()
        print(f"  ⏸️  Stopped at: {elapsed}")

        # Pause between cycles
        time.sleep(0.1)

    stats = sw.get_session_stats()
    print(f"\n📊 Total accumulated time: {stats['formatted']}")

def demo_formatting_options():
    """Demonstrate different time formatting options"""
    print("\n📝 FORMATTING OPTIONS DEMO")
    print("-" * 30)

    sw = Stopwatch()
    sw.start()
    time.sleep(1.234)  # 1.234 seconds
    sw.stop()

    print("Same time shown in different formats:")
    print(f"  Full:    {sw.get_formatted_time('full')}")
    print(f"  Short:   {sw.get_formatted_time('short')}")
    print(f"  Minimal: {sw.get_formatted_time('minimal')}")
    print(f"  Raw ms:  {sw.get_elapsed_time()}ms")

def demo_long_timing():
    """Demonstrate handling of longer time periods"""
    print("\n⏰ LONG TIMING SIMULATION")
    print("-" * 30)

    sw = Stopwatch()

    # Simulate long timing by directly setting elapsed time
    print("Simulating various time periods...")

    test_times = [
        (5000, "5 seconds"),
        (65000, "1 minute 5 seconds"),
        (3665000, "1 hour 1 minute 5 seconds"),
        (90061000, "25 hours 1 minute 1 second")
    ]

    for ms, description in test_times:
        sw.total_elapsed = ms
        formatted = sw.get_formatted_time()
        minimal = sw.get_formatted_time('minimal')
        print(f"  {description:25} → {formatted} ({minimal})")

def demo_session_statistics():
    """Demonstrate session statistics"""
    print("\n📈 SESSION STATISTICS DEMO")
    print("-" * 30)

    sw = Stopwatch()

    # Simulate a session with multiple starts/stops
    times = [0.2, 0.3, 0.5, 0.1]

    for i, duration in enumerate(times):
        sw.start()
        time.sleep(duration)
        sw.stop()
        print(f"  Segment {i+1}: {duration}s")

    stats = sw.get_session_stats()
    print(f"\nSession Summary:")
    print(f"  📊 Total time: {stats['formatted']}")
    print(f"  🕐 Hours: {stats['hours']}")
    print(f"  ⏱️  Minutes: {stats['minutes']}")
    print(f"  ⚡ Seconds: {stats['seconds']}")
    print(f"  💫 Milliseconds: {stats['milliseconds']}")
    print(f"  ▶️  Currently running: {stats['is_running']}")

def interactive_demo():
    """Interactive demonstration"""
    print("\n🎮 INTERACTIVE DEMO")
    print("-" * 30)
    print("Commands: start, stop, reset, time, stats, quit")

    sw = Stopwatch()

    while True:
        try:
            cmd = input("\nEnter command: ").strip().lower()

            if cmd == 'start':
                if sw.is_running():
                    print("⚠️  Already running!")
                else:
                    sw.start()
                    print("▶️  Started stopwatch")

            elif cmd == 'stop':
                if not sw.is_running():
                    print("⚠️  Not running!")
                else:
                    sw.stop()
                    print(f"⏸️  Stopped at: {sw.get_formatted_time()}")

            elif cmd == 'reset':
                sw.reset()
                print("🔄 Reset to 00:00:00.000")

            elif cmd == 'time':
                formatted = sw.get_formatted_time()
                status = "RUNNING" if sw.is_running() else "STOPPED"
                print(f"⏰ {formatted} ({status})")

            elif cmd == 'stats':
                stats = sw.get_session_stats()
                print(f"📊 Statistics:")
                print(f"   Time: {stats['formatted']}")
                print(f"   Running: {stats['is_running']}")
                print(f"   Raw ms: {stats['total_ms']}")

            elif cmd in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break

            else:
                print("❓ Unknown command. Try: start, stop, reset, time, stats, quit")

        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break

def main():
    """Run all demonstrations"""
    print("=" * 50)
    print("   CYD STOPWATCH - DEMONSTRATION")
    print("=" * 50)
    print("This demo shows the stopwatch functionality")
    print("without requiring CYD hardware.")

    try:
        demo_basic_timing()
        demo_start_stop_cycles()
        demo_formatting_options()
        demo_long_timing()
        demo_session_statistics()

        print("\n" + "=" * 50)
        print("🎉 All demonstrations completed!")
        print("Would you like to try the interactive demo? (y/n)")

        if input().strip().lower().startswith('y'):
            interactive_demo()

    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user. Goodbye! 👋")
    except Exception as e:
        print(f"\nError during demo: {e}")

if __name__ == "__main__":
    main()
