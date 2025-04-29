#!/usr/bin/env python3
"""
Utility script to check if all required dependencies for the Smart Fridge system
are installed and properly configured.
"""
import importlib
import sys
import os
import platform

# Required packages for the simulator
SIMULATOR_DEPENDENCIES = [
    {'name': 'requests', 'version': '2.28.1', 'import_name': 'requests'},
    {'name': 'python-dotenv', 'version': '0.21.0', 'import_name': 'dotenv'},
    {'name': 'schedule', 'version': '1.1.0', 'import_name': 'schedule'},
    {'name': 'flask', 'version': '2.2.2', 'import_name': 'flask'},
    {'name': 'pillow', 'version': '9.3.0', 'import_name': 'PIL'},
    {'name': 'numpy', 'version': '1.23.5', 'import_name': 'numpy'},
]

def check_python_version():
    """Check if Python version is compatible."""
    python_version = sys.version_info
    print(f"Python version: {sys.version}")
    
    if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 7):
        print("❌ WARNING: Python 3.7 or higher is recommended. Some features may not work correctly.")
        return False
    else:
        print("✅ Python version is compatible.")
        return True

def check_os_compatibility():
    """Check if the OS is compatible."""
    system = platform.system()
    print(f"Operating System: {platform.system()} {platform.release()}")
    
    if system == "Windows":
        print("✅ Running on Windows - Simulator mode is fully supported.")
        print("ℹ️ Note: Actual hardware functionality would require Raspberry Pi OS.")
        return True
    elif system == "Linux":
        if "raspbian" in platform.platform().lower() or "raspberry" in platform.platform().lower():
            print("✅ Running on Raspberry Pi OS - Both hardware and simulator modes are supported.")
        else:
            print("✅ Running on Linux - Simulator mode is fully supported.")
            print("ℹ️ Note: Actual hardware functionality would require Raspberry Pi OS.")
        return True
    elif system == "Darwin":  # macOS
        print("✅ Running on macOS - Simulator mode is fully supported.")
        print("ℹ️ Note: Actual hardware functionality would require Raspberry Pi OS.")
        return True
    else:
        print(f"⚠️ Unrecognized operating system: {system}. Compatibility is unknown.")
        return False

def check_dependencies():
    """Check if all required packages are installed and compatible."""
    missing_packages = []
    incompatible_versions = []

    print("\nChecking required packages:")
    for package in SIMULATOR_DEPENDENCIES:
        try:
            module = importlib.import_module(package['import_name'])
            try:
                version = module.__version__
                print(f"✅ {package['name']}: {version} (required: {package['version']})")
                
                # Check if version might be incompatible
                if version != package['version']:
                    print(f"   ⚠️ Installed version differs from recommended version.")
                    incompatible_versions.append(f"{package['name']}: {version} (recommended: {package['version']})")
            except AttributeError:
                print(f"✅ {package['name']}: installed (version attribute not found)")
        except ImportError:
            print(f"❌ {package['name']}: Not installed")
            missing_packages.append(package['name'])

    return missing_packages, incompatible_versions

def check_directories():
    """Check if required directories exist and are accessible."""
    print("\nChecking required directories:")
    
    # Check simulator mock_images directory
    simulator_mock_images = "simulator/mock_images"
    if os.path.exists(simulator_mock_images):
        if os.access(simulator_mock_images, os.W_OK):
            print(f"✅ {simulator_mock_images}: Exists and is writable")
        else:
            print(f"❌ {simulator_mock_images}: Exists but is not writable")
    else:
        print(f"❌ {simulator_mock_images}: Directory does not exist")
        try:
            os.makedirs(simulator_mock_images, exist_ok=True)
            print(f"✅ Created directory: {simulator_mock_images}")
        except Exception as e:
            print(f"❌ Failed to create directory: {e}")

def check_environment_files():
    """Check if environment files exist."""
    print("\nChecking environment files:")
    
    if os.path.exists(".env"):
        print("✅ .env file exists")
    else:
        print("ℹ️ .env file does not exist (not required but recommended for configuration)")

def print_installation_help(missing_packages):
    """Print help for installing missing packages."""
    if missing_packages:
        print("\n⚠️ Missing packages installation command:")
        packages_str = " ".join(missing_packages)
        print(f"\npip install {packages_str}")
        
        print("\nAlternatively, install all requirements using:")
        print("\npip install -r simulator/requirements.txt")

def main():
    """Main check function."""
    print("=" * 60)
    print("Smart Fridge System Dependencies Check")
    print("=" * 60)
    
    check_python_version()
    check_os_compatibility()
    missing_packages, incompatible_versions = check_dependencies()
    check_directories()
    check_environment_files()
    
    print("\n" + "=" * 60)
    print("Summary:")
    
    if not missing_packages and not incompatible_versions:
        print("✅ All dependencies are installed correctly!")
    else:
        if missing_packages:
            print(f"❌ Missing packages: {', '.join(missing_packages)}")
        if incompatible_versions:
            print("⚠️ Potentially incompatible package versions:")
            for pkg in incompatible_versions:
                print(f"   - {pkg}")
    
    print("=" * 60)
    
    if missing_packages:
        print_installation_help(missing_packages)
    
    return 0 if not missing_packages else 1

if __name__ == "__main__":
    sys.exit(main()) 