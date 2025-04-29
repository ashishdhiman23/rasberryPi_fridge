"""
API communication module for Smart Fridge Raspberry Pi system.
Handles sending data to the backend API.
"""
import requests
import logging
import time
import base64
from config import UPLOAD_ENDPOINT, UPLOAD_RETRY_DELAY, MAX_UPLOAD_RETRIES

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='fridge_monitor.log'
)
logger = logging.getLogger('api')


def upload_data(sensor_data, image_base64):
    """
    Upload sensor data and captured image to the API using multipart/form-data
    
    Args:
        sensor_data (dict): Dictionary with temperature, humidity, and gas readings
        image_base64 (str): Base64 encoded image string
    
    Returns:
        bool: True if upload was successful, False otherwise
    """
    if not image_base64:
        logger.error("No image data to upload")
        return False
    
    # Try to upload with retries
    for attempt in range(MAX_UPLOAD_RETRIES):
        try:
            logger.info(f"Uploading data to {UPLOAD_ENDPOINT} (Attempt {attempt + 1}/{MAX_UPLOAD_RETRIES})")
            
            # Convert base64 string to binary data for more efficient transfer
            try:
                # Remove 'data:image/jpeg;base64,' prefix if present
                if ';base64,' in image_base64:
                    image_base64 = image_base64.split(';base64,')[1]
                
                # Decode base64 to binary
                image_binary = base64.b64decode(image_base64)
            except Exception as e:
                logger.error(f"Failed to decode base64 image: {str(e)}")
                return False
            
            # Create multipart/form-data payload
            files = {
                'image': ('fridge.jpg', image_binary, 'image/jpeg')
            }
            
            # Add sensor data as form fields
            data = {
                'temp': str(sensor_data["temp"]),
                'humidity': str(sensor_data["humidity"]),
                'gas': str(sensor_data["gas"])
            }
            
            # Send data using multipart/form-data
            response = requests.post(
                UPLOAD_ENDPOINT,
                files=files,
                data=data,
                timeout=30  # 30 seconds timeout
            )
            
            if response.status_code == 200:
                logger.info("Data uploaded successfully")
                logger.info(f"API response: {response.json()}")
                return True
            else:
                logger.error(f"API returned error: {response.status_code}")
                logger.error(f"Response: {response.text}")
        
        except requests.exceptions.ConnectionError:
            logger.error("Connection error - API server may be unavailable")
        except requests.exceptions.Timeout:
            logger.error("Request timed out - API server may be overloaded")
        except Exception as e:
            logger.error(f"Unexpected error during upload: {str(e)}")
        
        # Wait before retrying
        if attempt < MAX_UPLOAD_RETRIES - 1:
            logger.info(f"Retrying in {UPLOAD_RETRY_DELAY} seconds...")
            time.sleep(UPLOAD_RETRY_DELAY)
    
    logger.error("All upload attempts failed")
    return False 