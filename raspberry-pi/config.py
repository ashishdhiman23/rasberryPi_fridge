"""
Configuration settings for the Smart Fridge Raspberry Pi module.
"""
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Raspberry Pi configuration settings

# API settings
API_BASE_URL = "https://smart-fridge-backend.onrender.com/api"
# Use multipart endpoint for more efficient uploads
UPLOAD_ENDPOINT = f"{API_BASE_URL}/upload/multipart"
UPLOAD_RETRY_DELAY = 10  # seconds
MAX_UPLOAD_RETRIES = 3

# Sensor pin definitions
DHT_PIN = 4  # GPIO pin for DHT22 sensor
MCP3008_CLK = 11
MCP3008_MISO = 9
MCP3008_MOSI = 10
MCP3008_CS = 8
GAS_CHANNEL = 0  # MCP3008 channel for gas sensor

# Camera settings
CAMERA_RESOLUTION = (1024, 768)
CAMERA_ROTATION = 0
CAMERA_FRAMERATE = 15

# Monitoring settings
MONITORING_INTERVAL = 30  # seconds
IMAGE_CAPTURE_INTERVAL = 300  # seconds 