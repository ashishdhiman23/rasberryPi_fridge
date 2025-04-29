#!/usr/bin/env python3
"""
Run the Smart Fridge API server.
This allows users to chat with their fridge using GPT-4.
"""
import os
import sys
import argparse
import uvicorn
from dotenv import load_dotenv

# Set up the Python path to include the project root
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
load_dotenv()

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Run Smart Fridge API Server")
    parser.add_argument(
        "--host", 
        type=str, 
        default="127.0.0.1", 
        help="Host to bind the server to (default: 127.0.0.1)"
    )
    parser.add_argument(
        "--port", 
        type=int, 
        default=8000, 
        help="Port to bind the server to (default: 8000)"
    )
    parser.add_argument(
        "--reload", 
        action="store_true", 
        help="Enable auto-reload for development"
    )
    
    return parser.parse_args()

def main():
    """Run the API server."""
    if not os.getenv("OPENAI_API_KEY"):
        print("WARNING: OPENAI_API_KEY environment variable not set.")
        print("The chat feature will not work without an API key.")
        print("You can set it in a .env file or as an environment variable.")
        # Continue anyway to allow testing other API features
    
    args = parse_args()
    
    print(f"Starting Smart Fridge API server at http://{args.host}:{args.port}")
    print("Press Ctrl+C to exit")
    
    # Run the server
    uvicorn.run(
        "simulator.api:app", 
        host=args.host, 
        port=args.port,
        reload=args.reload
    )
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 