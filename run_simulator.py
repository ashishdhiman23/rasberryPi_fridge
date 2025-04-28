#!/usr/bin/env python3
"""
Wrapper script to run the Smart Fridge Simulator.
Ensures the paths are correctly set up when run from project root.
"""
import os
import sys

# Set up the Python path to include the project root
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Run the simulator
from simulator.simulator import run

if __name__ == "__main__":
    sys.exit(run()) 