"""
Boot configuration for CYD Planter Sensor
=========================================

This file runs automatically when MicroPython starts.
Sets up basic system configuration before main.py runs.
"""

import gc
import time
from machine import freq

# Increase CPU frequency for better performance
freq(240000000)  # 240MHz

# Enable garbage collection
gc.enable()

# Initial garbage collection
gc.collect()

print("CYD Planter Sensor - System initialized")
print(f"Free memory: {gc.mem_free()} bytes")
print(f"CPU frequency: {freq()} Hz")

# Small delay before main application
time.sleep_ms(100)
