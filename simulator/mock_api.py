"""
Mock API module for Smart Fridge Simulator.
Simulates uploading data to a backend API without requiring actual connection.
"""
import time
import json
import random
import logging
import requests
from datetime import datetime
from simulator.config import UPLOAD_ENDPOINT, UPLOAD_RETRY_DELAY, MAX_UPLOAD_RETRIES

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='simulator.log'
)
logger = logging.getLogger('mock_api')


def upload_data(sensor_data, image_base64=None, use_real_api=False):
    """
    Upload sensor data and image to API
    
    Args:
        sensor_data (dict): Dictionary containing sensor readings
        image_base64 (str, optional): Base64 encoded image string
        use_real_api (bool): Whether to use the real API endpoint or simulate
        
    Returns:
        bool: True if upload successful (or simulated success), False otherwise
    """
    if use_real_api:
        return upload_to_real_api(sensor_data, image_base64)
    else:
        return simulate_upload(sensor_data, image_base64)


def simulate_upload(sensor_data, image_base64=None):
    """
    Simulate uploading data to API with random success/failure
    
    Args:
        sensor_data (dict): Dictionary containing sensor readings
        image_base64 (str, optional): Base64 encoded image string
        
    Returns:
        bool: True if simulated upload successful, False otherwise
    """
    logger.info("Simulating API upload...")
    
    # Prepare data for logging
    upload_data = {
        "timestamp": datetime.now().isoformat(),
        "sensor_data": sensor_data
    }
    
    if image_base64:
        upload_data["has_image"] = True
    
    # Simulate network delay
    delay = random.uniform(0.5, 2.0)
    time.sleep(delay)
    
    # Simulate occasional failures (10% chance)
    if random.random() < 0.1:
        logger.error("Simulated network error during upload")
        return False
    
    # Log the data that would be sent
    logger.info(f"Mock API upload success after {delay:.2f}s delay")
    logger.debug(f"Data that would be sent: {json.dumps(upload_data)}")
    
    # Save mock data to local file for inspection
    try:
        with open("simulator/last_upload.json", "w") as f:
            json.dump(upload_data, f, indent=2)
    except Exception as e:
        logger.warning(f"Failed to save mock upload data: {str(e)}")
        
    return True


def upload_to_real_api(sensor_data, image_base64=None):
    """
    Upload sensor data and image to real API endpoint
    
    Args:
        sensor_data (dict): Dictionary containing sensor readings
        image_base64 (str, optional): Base64 encoded image string
        
    Returns:
        bool: True if upload successful, False otherwise
    """
    # Prepare payload
    payload = {
        "timestamp": datetime.now().isoformat(),
        "temperature": sensor_data.get("temp"),
        "humidity": sensor_data.get("humidity"),
        "gas_level": sensor_data.get("gas")
    }
    
    if image_base64:
        payload["image"] = image_base64
    
    # Attempt upload with retries
    retries = 0
    while retries <= MAX_UPLOAD_RETRIES:
        try:
            logger.info(f"Uploading data to {UPLOAD_ENDPOINT}, attempt {retries+1}")
            
            response = requests.post(
                UPLOAD_ENDPOINT,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if response.status_code == 200:
                logger.info("Upload successful")
                return True
            else:
                logger.error(f"Upload failed: HTTP {response.status_code}, {response.text}")
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Upload error: {str(e)}")
        
        # Increment retry counter
        retries += 1
        if retries <= MAX_UPLOAD_RETRIES:
            logger.info(f"Retrying in {UPLOAD_RETRY_DELAY} seconds...")
            time.sleep(UPLOAD_RETRY_DELAY)
    
    logger.error(f"Upload failed after {MAX_UPLOAD_RETRIES} retries")
    return False 