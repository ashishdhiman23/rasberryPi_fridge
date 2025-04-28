"""
Mock camera module for Smart Fridge Simulator.
Generates synthetic fridge images without requiring actual camera hardware.
"""
import os
import time
import random
import base64
import logging
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from io import BytesIO
from simulator.config import MOCK_IMAGE_WIDTH, MOCK_IMAGE_HEIGHT, MOCK_IMAGE_PATH

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='simulator.log'
)
logger = logging.getLogger('mock_camera')

# Check if mock images directory exists, create if not
os.makedirs(MOCK_IMAGE_PATH, exist_ok=True)

# Store the last generated image path
last_image_path = None


def initialize_camera():
    """Mock initialization of camera"""
    logger.info("Initializing mock camera...")
    logger.info("Mock camera initialized successfully")
    return True


def generate_mock_fridge_image():
    """
    Generate a synthetic image of a refrigerator interior
    
    Returns:
        PIL.Image: A synthetic fridge interior image
    """
    # Create base image with light blue-white gradient (fridge color)
    img = Image.new('RGB', (MOCK_IMAGE_WIDTH, MOCK_IMAGE_HEIGHT), color=(240, 248, 255))
    draw = ImageDraw.Draw(img)
    
    # Draw fridge shelves
    for shelf_y in range(150, MOCK_IMAGE_HEIGHT, 150):
        # Draw shelf
        draw.rectangle(
            [(0, shelf_y), (MOCK_IMAGE_WIDTH, shelf_y + 10)], 
            fill=(200, 200, 210)
        )
        
        # Add random food items on each shelf
        num_items = random.randint(1, 5)
        for _ in range(num_items):
            item_x = random.randint(50, MOCK_IMAGE_WIDTH - 100)
            item_y = shelf_y - random.randint(30, 120)
            item_width = random.randint(40, 100)
            item_height = random.randint(40, 100)
            
            # Random food item colors
            item_color = (
                random.randint(50, 250),
                random.randint(50, 250),
                random.randint(50, 250)
            )
            
            # Draw food item
            draw.rectangle(
                [(item_x, item_y), (item_x + item_width, item_y + item_height)],
                fill=item_color,
                outline=(30, 30, 30)
            )
    
    # Add timestamp to image
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    try:
        # Try to use a font, fall back to default if not available
        font = ImageFont.truetype("arial.ttf", 20)
        draw.text((10, 10), f"Mock Fridge - {timestamp}", fill=(50, 50, 50), font=font)
    except IOError:
        # Use default font if arial is not available
        draw.text((10, 10), f"Mock Fridge - {timestamp}", fill=(50, 50, 50))
    
    # Add some noise and blur to make it more realistic
    img = img.filter(ImageFilter.GaussianBlur(radius=0.5))
    
    # Return the image
    return img


def capture_image():
    """
    Generate a mock fridge image and return as base64 string
    
    Returns:
        str: Base64 encoded image or None if capture fails
    """
    global last_image_path
    
    try:
        logger.info("Capturing mock fridge image...")
        
        # Simulate occasional camera failure (5% chance)
        if random.random() < 0.05:
            logger.error("Simulating camera failure")
            return None
        
        # Generate synthetic image
        img = generate_mock_fridge_image()
        
        # Save image to file with timestamp
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = f"fridge_{timestamp}.jpg"
        file_path = os.path.join(MOCK_IMAGE_PATH, filename)
        img.save(file_path, format="JPEG", quality=85)
        last_image_path = file_path
        
        # Convert to base64 for API upload
        buffered = BytesIO()
        img.save(buffered, format="JPEG")
        img_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
        
        logger.info(f"Mock image captured and saved to {file_path}")
        return img_base64
        
    except Exception as e:
        logger.error(f"Error capturing mock image: {str(e)}")
        return None


def cleanup():
    """Mock cleanup of camera resources"""
    logger.info("Mock camera cleanup completed")
    return True 