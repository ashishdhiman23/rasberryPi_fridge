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
    
    # Common food items with colors
    common_foods = [
        {"name": "milk", "color": (250, 250, 250), "size": (60, 120)},
        {"name": "orange juice", "color": (255, 180, 0), "size": (60, 120)},
        {"name": "apple", "color": (220, 0, 0), "size": (50, 50)},
        {"name": "orange", "color": (255, 165, 0), "size": (50, 50)},
        {"name": "yogurt", "color": (250, 250, 240), "size": (40, 60)},
        {"name": "cheese", "color": (255, 255, 150), "size": (80, 40)},
        {"name": "lettuce", "color": (100, 220, 50), "size": (100, 60)},
        {"name": "tomato", "color": (220, 60, 50), "size": (45, 45)},
        {"name": "carrot", "color": (250, 160, 0), "size": (30, 100)},
        {"name": "eggs", "color": (255, 250, 240), "size": (100, 50)},
        {"name": "butter", "color": (250, 230, 140), "size": (70, 40)},
        {"name": "leftover pasta", "color": (230, 230, 200), "size": (90, 70)},
        {"name": "chicken", "color": (240, 220, 180), "size": (100, 60)},
        {"name": "broccoli", "color": (50, 180, 50), "size": (70, 70)},
        {"name": "soda", "color": (150, 150, 150), "size": (45, 110)},
        {"name": "cucumber", "color": (100, 180, 80), "size": (40, 120)},
        {"name": "bell pepper", "color": (200, 50, 50), "size": (60, 60)},
        {"name": "ketchup", "color": (200, 30, 30), "size": (50, 100)}
    ]
    
    # Randomly select food items to place on each shelf
    foods_placed = []
    
    for shelf_y in range(150, MOCK_IMAGE_HEIGHT, 150):
        shelf_items = random.randint(2, 5)  # 2-5 items per shelf
        
        for _ in range(shelf_items):
            # Get random food item
            food = random.choice(common_foods)
            foods_placed.append(food["name"])
            
            # Position on shelf
            item_x = random.randint(20, MOCK_IMAGE_WIDTH - food["size"][0] - 20)
            item_y = shelf_y - random.randint(30, min(140, food["size"][1] + 60))
            
            # Add some random variation to color
            color_variation = random.randint(-20, 20)
            food_color = tuple(
                max(0, min(255, c + color_variation))
                for c in food["color"]
            )
            
            # Draw food item
            draw.rectangle(
                [(item_x, item_y), 
                 (item_x + food["size"][0], item_y + food["size"][1])],
                fill=food_color,
                outline=(30, 30, 30)
            )
            
            # Add label
            try:
                # Try to use a font, fall back to default if not available
                font = ImageFont.truetype("arial.ttf", 12)
                draw.text(
                    (item_x + 5, item_y + 5),
                    food["name"],
                    fill=(10, 10, 10),
                    font=font
                )
            except IOError:
                # Use default font if arial is not available
                draw.text(
                    (item_x + 5, item_y + 5),
                    food["name"],
                    fill=(10, 10, 10)
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
    
    # Log what foods are in the image for debugging
    logger.info(f"Generated fridge image with: {', '.join(foods_placed)}")
    
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