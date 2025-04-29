#!/usr/bin/env python3
"""
Script to run the backend API server for the Smart Fridge system.
This server handles API endpoints, including the chat functionality.
"""
import os
import sys
import subprocess


def check_openai_key():
    """Check if OPENAI_API_KEY is set in environment or .env file"""
    if os.environ.get("OPENAI_API_KEY"):
        return True
    
    # Check if .env file exists in backend directory
    env_path = os.path.join("backend", ".env")
    if os.path.exists(env_path):
        with open(env_path, "r") as f:
            for line in f:
                if (line.strip().startswith("OPENAI_API_KEY=") and 
                    len(line.strip()) > 14):
                    return True
    
    return False


def main():
    # Change to the backend directory
    backend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                              "backend")
    os.chdir(backend_dir)
    
    # Check for OpenAI API key
    if not check_openai_key():
        print("\033[91mWARNING: OPENAI_API_KEY not found!\033[0m")
        print("The chat functionality will not work without an OpenAI API key.")
        print("Please set the OPENAI_API_KEY in the backend/.env file.")
        user_input = input("Continue anyway? (y/n): ")
        if user_input.lower() != "y":
            sys.exit(1)
    
    print("\033[92mStarting backend server...\033[0m")
    print("Access the dashboard at http://localhost:8000")
    
    # Run the backend server
    try:
        # Using sys.executable ensures we use the same Python interpreter
        subprocess.run([sys.executable, "main.py"], check=True)
    except KeyboardInterrupt:
        print("\n\033[92mServer stopped\033[0m")
    except Exception as e:
        print(f"\033[91mError running server: {e}\033[0m")
        sys.exit(1)


if __name__ == "__main__":
    main() 