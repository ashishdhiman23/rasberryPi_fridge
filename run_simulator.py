#!/usr/bin/env python3
"""
Script to run the Smart Fridge Simulator.
The simulator emulates sensor data and camera for testing without hardware.
"""
import sys
import argparse
import subprocess


def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='Smart Fridge Simulator')
    
    parser.add_argument(
        '--interval', 
        type=int, 
        default=30,
        help='Monitoring interval in seconds (default: 30)'
    )
    
    parser.add_argument(
        '--image-interval', 
        type=int, 
        default=60,
        help='Image capture interval in seconds (default: 60)'
    )
    
    parser.add_argument(
        '--real-api', 
        action='store_true',
        help='Use real API endpoint instead of simulating'
    )
    
    return parser.parse_args()


def main():
    args = parse_arguments()
    
    # Construct command with arguments
    cmd = [sys.executable, "-m", "simulator.simulator"]
    
    if args.interval:
        cmd.extend(["--interval", str(args.interval)])
    
    if args.image_interval:
        cmd.extend(["--image-interval", str(args.image_interval)])
    
    if args.real_api:
        cmd.append("--real-api")
    
    print("\033[92mStarting Smart Fridge Simulator...\033[0m")
    print(f"Monitoring interval: {args.interval} seconds")
    print(f"Image capture interval: {args.image_interval} seconds")
    print(f"Using real API: {'Yes' if args.real_api else 'No'}")
    
    try:
        # Run the simulator with the provided arguments
        subprocess.run(cmd, check=True)
    except KeyboardInterrupt:
        print("\n\033[92mSimulator stopped\033[0m")
    except Exception as e:
        print(f"\033[91mError running simulator: {e}\033[0m")
        sys.exit(1)


if __name__ == "__main__":
    main() 