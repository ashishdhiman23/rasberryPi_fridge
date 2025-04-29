#!/usr/bin/env python3
"""
Start script for Smart Fridge system.
Launches both the simulator and the API server for the dashboard.
"""
import os
import sys
import argparse
import subprocess
import time
from pathlib import Path

# Add project root to Python path
current_dir = Path(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, str(current_dir))

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Start Smart Fridge System")
    
    parser.add_argument(
        "--host", 
        type=str, 
        default="127.0.0.1", 
        help="Host to bind the API server to (default: 127.0.0.1)"
    )
    
    parser.add_argument(
        "--port", 
        type=int, 
        default=8000, 
        help="Port to bind the API server to (default: 8000)"
    )
    
    parser.add_argument(
        "--interval", 
        type=int, 
        default=30, 
        help="Monitoring interval in seconds (default: 30)"
    )
    
    parser.add_argument(
        "--image-interval", 
        type=int, 
        default=60, 
        help="Image capture interval in seconds (default: 60)"
    )
    
    parser.add_argument(
        "--no-simulator", 
        action="store_true", 
        help="Don't start the simulator, only the API server"
    )
    
    parser.add_argument(
        "--real-api", 
        action="store_true", 
        help="Use real API endpoint for uploads"
    )
    
    parser.add_argument(
        "--debug", 
        action="store_true", 
        help="Run in debug mode with auto-reload"
    )
    
    return parser.parse_args()

def check_dependencies():
    """Check if required packages are installed."""
    try:
        # Check for simulator dependencies
        import schedule
        import PIL
        
        # Check for API server dependencies
        import fastapi
        import uvicorn
        import httpx
        
        return True
    except ImportError as e:
        print(f"Missing dependency: {e}")
        print("Please install required packages:")
        print("    pip install -r simulator/requirements.txt")
        return False

def start_simulator(args):
    """Start the simulator in a separate process."""
    print("Starting Smart Fridge Simulator...")
    
    simulator_cmd = [
        sys.executable,
        "run_simulator.py",
        "--interval", str(args.interval),
        "--image-interval", str(args.image_interval)
    ]
    
    if args.real_api:
        simulator_cmd.append("--real-api")
    
    try:
        simulator_process = subprocess.Popen(
            simulator_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1
        )
        
        # Start a thread to read and print simulator output
        import threading
        def print_output(process):
            for line in process.stdout:
                print(f"[Simulator] {line.strip()}")
        
        thread = threading.Thread(target=print_output, args=(simulator_process,))
        thread.daemon = True
        thread.start()
        
        return simulator_process
    except Exception as e:
        print(f"Error starting simulator: {e}")
        return None

def start_api_server(args):
    """Start the API server for the dashboard."""
    print(f"Starting Smart Fridge API Server at http://{args.host}:{args.port}")
    print("Dashboard will be available at: " + 
          f"http://{args.host}:{args.port}/dashboard/index.html")
    
    server_cmd = [
        sys.executable,
        "run_api.py",
        "--host", args.host,
        "--port", str(args.port)
    ]
    
    if args.debug:
        server_cmd.append("--reload")
    
    try:
        api_process = subprocess.Popen(
            server_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1
        )
        
        # Start a thread to read and print API server output
        import threading
        def print_output(process):
            for line in process.stdout:
                print(f"[API Server] {line.strip()}")
        
        thread = threading.Thread(target=print_output, args=(api_process,))
        thread.daemon = True
        thread.start()
        
        return api_process
    except Exception as e:
        print(f"Error starting API server: {e}")
        return None

def main():
    """Main entry point."""
    args = parse_args()
    
    # Check dependencies
    if not check_dependencies():
        return 1
    
    simulator_process = None
    api_process = None
    
    try:
        # Start simulator if requested
        if not args.no_simulator:
            simulator_process = start_simulator(args)
            if not simulator_process:
                return 1
        
        # Give the simulator a moment to initialize
        time.sleep(2)
        
        # Start API server
        api_process = start_api_server(args)
        if not api_process:
            return 1
        
        print("\n" + "="*70)
        print(f"Smart Fridge System is running!")
        print(f"Dashboard URL: http://{args.host}:{args.port}/dashboard/index.html")
        print("="*70)
        print("\nPress Ctrl+C to stop all services...")
        
        # Wait for user to press Ctrl+C
        while True:
            time.sleep(1)
    
    except KeyboardInterrupt:
        print("\nShutting down Smart Fridge System...")
    finally:
        # Clean up processes
        if simulator_process:
            print("Stopping simulator...")
            simulator_process.terminate()
            simulator_process.wait(timeout=5)
        
        if api_process:
            print("Stopping API server...")
            api_process.terminate()
            api_process.wait(timeout=5)
        
        print("Shutdown complete.")
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 