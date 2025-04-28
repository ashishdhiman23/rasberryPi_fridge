"""
Configuration settings for the Smart Fridge Raspberry Pi module.
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# API Settings
API_BASE_URL = os.getenv('API_BASE_URL', 'http://localhost:8000/api')
UPLOAD_ENDPOINT = f"{API_BASE_URL}/upload"

# Sensor Pins (BCM numbering)
DHT_PIN = 4  # Temperature and humidity sensor
MCP3008_CLK = 11
MCP3008_MISO = 9
MCP3008_MOSI = 10
MCP3008_CS = 8
GAS_CHANNEL = 0  # MQ-5 gas sensor on channel 0 of MCP3008

# Camera Settings
CAMERA_RESOLUTION = (1024, 768)
CAMERA_ROTATION = 0  # Adjust based on camera mounting (0, 90, 180, 270)
CAMERA_FRAMERATE = 15

# Monitoring Settings
MONITORING_INTERVAL = 30  # seconds between readings
IMAGE_CAPTURE_INTERVAL = 60 * 30  # Take photo every 30 minutes
UPLOAD_RETRY_DELAY = 10  # seconds to wait before retrying upload
MAX_UPLOAD_RETRIES = 3 