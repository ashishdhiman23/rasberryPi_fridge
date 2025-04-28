"""
Camera module for Smart Fridge Raspberry Pi system.
Handles image capture and processing.
"""
import io
import time
import base64
import logging
from picamera import PiCamera
from PIL import Image
import numpy as np
from config import CAMERA_RESOLUTION, CAMERA_ROTATION, CAMERA_FRAMERATE

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='fridge_monitor.log'
)
logger = logging.getLogger('camera')

# Camera instance
camera = None


def initialize_camera():
    """Initialize the Raspberry Pi camera"""
    global camera
    
    try:
        logger.info("Initializing camera...")
        camera = PiCamera()
        camera.resolution = CAMERA_RESOLUTION
        camera.rotation = CAMERA_ROTATION
        camera.framerate = CAMERA_FRAMERATE
        
        # Allow camera to warm up
        time.sleep(2)
        logger.info("Camera initialized successfully")
        return True
    except Exception as e:
        logger.error(f"Error initializing camera: {str(e)}")
        return False


def capture_image():
    """
    Capture an image from the camera
    
    Returns:
        str: Base64 encoded image string or None if capture fails
    """
    if camera is None:
        logger.error("Camera not initialized")
        return None
    
    try:
        # Create in-memory stream
        stream = io.BytesIO()
        
        # Capture the image to the stream
        logger.info("Capturing image...")
        camera.capture(stream, format='jpeg', quality=85)
        
        # Reset stream position
        stream.seek(0)
        
        # Convert to base64 for API transmission
        image_data = stream.read()
        base64_image = base64.b64encode(image_data).decode('utf-8')
        
        logger.info(f"Image captured successfully ({len(base64_image)} bytes)")
        return base64_image
    
    except Exception as e:
        logger.error(f"Error capturing image: {str(e)}")
        return None


def cleanup():
    """Clean up camera resources"""
    global camera
    
    if camera is not None:
        try:
            camera.close()
            camera = None
            logger.info("Camera cleanup completed")
        except Exception as e:
            logger.error(f"Error during camera cleanup: {str(e)}") 