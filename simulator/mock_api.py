"""
Mock module to simulate uploading data to a backend API.
"""
import json
import logging
import random
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, Union

import requests
from PIL import Image

from simulator.config import (
    MAX_UPLOAD_RETRIES,
    UPLOAD_ENDPOINT,
    UPLOAD_RETRY_DELAY,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def upload_data(
    sensor_data: Dict[str, float], image_path: Optional[Path] = None
) -> bool:
    """
    Simulate uploading sensor data and image to the backend API.

    Args:
        sensor_data: Dictionary containing sensor readings
        image_path: Path to the image file (optional)

    Returns:
        bool: True if upload was successful, False otherwise
    """
    # Add timestamp to data
    data = sensor_data.copy()
    data["timestamp"] = datetime.now().isoformat()

    # Log the data being uploaded
    logger.info(f"Uploading data: {data}")
    if image_path:
        logger.info(f"Uploading image: {image_path}")

    # Simulate upload to API, with random success/failure
    return simulate_upload() or upload_to_real_api(data, image_path)


def simulate_upload() -> bool:
    """
    Simulate an API call with random success/failure.

    Returns:
        bool: True if successful, False otherwise
    """
    # Simulate network delay
    time.sleep(random.uniform(0.5, 2.0))

    # 80% chance of success
    return random.random() < 0.8


def upload_to_real_api(
    data: Dict[str, Union[float, str]], image_path: Optional[Path] = None
) -> bool:
    """
    Upload data to the real API endpoint using multipart/form-data.

    Args:
        data: Dictionary containing sensor readings and timestamp
        image_path: Path to the image file (optional)

    Returns:
        bool: True if upload was successful, False otherwise
    """
    # Always use the multipart endpoint from config
    api_url = UPLOAD_ENDPOINT

    # Prepare the multipart form data
    payload = {"data": json.dumps(data)}

    # Add image file if provided
    if image_path and image_path.exists():
        try:
            # Ensure the image can be opened before attempting upload
            with Image.open(image_path) as img:
                img_format = img.format
                logger.debug(f"Image format: {img_format}, size: {img.size}")
            
            # Attempt to upload with retries
            for attempt in range(MAX_UPLOAD_RETRIES):
                try:
                    # Open file handle within the retry loop
                    with open(image_path, "rb") as img_file:
                        files = {
                            "image": (
                                image_path.name, 
                                img_file, 
                                f"image/{img_format.lower()}"
                            )
                        }
                        
                        response = requests.post(
                            api_url, 
                            data=payload, 
                            files=files, 
                            timeout=10
                        )
                    
                    if response.status_code == 200:
                        logger.info(f"Successfully uploaded data to {api_url}")
                        return True
                    else:
                        logger.warning(
                            f"Upload failed (attempt {attempt+1}/{MAX_UPLOAD_RETRIES}): "
                            f"Status {response.status_code}, Response: {response.text}"
                        )
                except requests.exceptions.RequestException as e:
                    logger.warning(
                        f"Upload request failed (attempt {attempt+1}/"
                        f"{MAX_UPLOAD_RETRIES}): {e}"
                    )
                
                # Wait before retrying
                if attempt < MAX_UPLOAD_RETRIES - 1:
                    time.sleep(UPLOAD_RETRY_DELAY)
            
            logger.error(f"Failed to upload data after {MAX_UPLOAD_RETRIES} attempts")
            return False
                
        except Exception as e:
            logger.error(f"Error processing image for upload: {e}")
            return False
    else:
        # No image to upload, just send the data
        for attempt in range(MAX_UPLOAD_RETRIES):
            try:
                response = requests.post(
                    api_url, 
                    data=payload, 
                    timeout=10
                )
                
                if response.status_code == 200:
                    logger.info(f"Successfully uploaded data to {api_url}")
                    return True
                else:
                    logger.warning(
                        f"Upload failed (attempt {attempt+1}/{MAX_UPLOAD_RETRIES}): "
                        f"Status {response.status_code}, Response: {response.text}"
                    )
            except requests.exceptions.RequestException as e:
                logger.warning(
                    f"Upload request failed (attempt {attempt+1}/"
                    f"{MAX_UPLOAD_RETRIES}): {e}"
                )
            
            # Wait before retrying
            if attempt < MAX_UPLOAD_RETRIES - 1:
                time.sleep(UPLOAD_RETRY_DELAY)
        
        logger.error(f"Failed to upload data after {MAX_UPLOAD_RETRIES} attempts")
        return False 