"""
Configuration settings for the Smart Fridge Simulator.
"""
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Simulator configuration settings

# API settings
API_BASE_URL = "https://smart-fridge-backend.onrender.com/api"
# Use multipart endpoint for more efficient uploads
UPLOAD_ENDPOINT = f"{API_BASE_URL}/upload/multipart"
UPLOAD_RETRY_DELAY = 10  # seconds
MAX_UPLOAD_RETRIES = 3

# Mock sensor settings
DEFAULT_TEMP = 4.0  # Default temperature in Celsius
DEFAULT_HUMIDITY = 50.0  # Default humidity percentage
DEFAULT_GAS = 100  # Default gas level in PPM

# Temperature and humidity variation ranges
TEMP_MIN = 2.0
TEMP_MAX = 8.0
HUMIDITY_MIN = 30.0
HUMIDITY_MAX = 70.0
GAS_MIN = 50
GAS_MAX = 250

# Mock camera settings
MOCK_IMAGE_WIDTH = 800
MOCK_IMAGE_HEIGHT = 600
MOCK_IMAGE_PATH = "simulator/mock_images"

# Monitoring settings
MONITORING_INTERVAL = 30  # seconds
IMAGE_CAPTURE_INTERVAL = 300  # seconds 