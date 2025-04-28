"""
Configuration settings for the Smart Fridge Simulator.
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# API Settings
API_BASE_URL = os.getenv('API_BASE_URL', 'http://localhost:8000/api')
UPLOAD_ENDPOINT = f"{API_BASE_URL}/upload"

# Mock Sensor Settings
DEFAULT_TEMP = 4.0  # Default fridge temperature in Celsius
DEFAULT_HUMIDITY = 50.0  # Default humidity percentage
DEFAULT_GAS = 100  # Default gas level in PPM

# Temperature variation range (Celsius)
TEMP_MIN = 2.0
TEMP_MAX = 8.0

# Humidity variation range (percentage)
HUMIDITY_MIN = 30.0
HUMIDITY_MAX = 70.0

# Gas level variation range (PPM)
GAS_MIN = 50
GAS_MAX = 300

# Mock Camera Settings
MOCK_IMAGE_WIDTH = 800
MOCK_IMAGE_HEIGHT = 600
MOCK_IMAGE_PATH = "simulator/mock_images"

# Monitoring Settings
MONITORING_INTERVAL = 30  # seconds between readings
IMAGE_CAPTURE_INTERVAL = 60 * 5  # Take photo every 5 minutes (shortened for testing)
UPLOAD_RETRY_DELAY = 10  # seconds to wait before retrying upload
MAX_UPLOAD_RETRIES = 3 