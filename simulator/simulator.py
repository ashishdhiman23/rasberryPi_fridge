#!/usr/bin/env python3
"""
Main script for Smart Fridge Simulator.
Emulates the behavior of a Raspberry Pi-based smart fridge monitoring system.
"""
import os
import time
import signal
import sys
import logging
import argparse
import schedule
from datetime import datetime

# Import mock modules
from simulator import mock_sensors, mock_camera, mock_api
from simulator.config import (
    MONITORING_INTERVAL, 
    IMAGE_CAPTURE_INTERVAL
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='simulator.log',
    filemode='a'
)
console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)

logger = logging.getLogger('simulator')

# Control variables
running = True
last_image_capture = 0
use_real_api = False


def signal_handler(sig, frame):
    """Handle Ctrl+C and other termination signals"""
    global running
    logger.info("Shutdown signal received, cleaning up...")
    running = False


def initialize():
    """Initialize all components"""
    # Register signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Initialize mock sensors and camera
    if not mock_sensors.initialize_sensors():
        logger.error("Failed to initialize mock sensors, exiting...")
        return False
    
    if not mock_camera.initialize_camera():
        logger.error("Failed to initialize mock camera, exiting...")
        mock_sensors.cleanup()
        return False
    
    logger.info("Simulator initialized successfully")
    return True


def cleanup():
    """Clean up resources before exiting"""
    logger.info("Cleaning up resources...")
    mock_sensors.cleanup()
    mock_camera.cleanup()
    logger.info("Cleanup complete, exiting...")


def monitoring_cycle():
    """Run a complete monitoring cycle"""
    global last_image_capture
    
    try:
        current_time = time.time()
        logger.info("Starting monitoring cycle...")
        
        # Read sensor data
        sensor_data = mock_sensors.read_all_sensors()
        logger.info(f"Sensors: Temp={sensor_data['temp']}°C, " 
                   f"Humidity={sensor_data['humidity']}%, "
                   f"Gas={sensor_data['gas']} PPM")
        
        # Decide if we need to capture an image
        capture_now = current_time - last_image_capture >= IMAGE_CAPTURE_INTERVAL
        
        if capture_now:
            # Capture image
            image_base64 = mock_camera.capture_image()
            
            if image_base64:
                # Update last capture time
                last_image_capture = current_time
                
                # Upload data to API
                if mock_api.upload_data(sensor_data, image_base64, use_real_api):
                    logger.info("Monitoring cycle completed successfully with image")
                else:
                    logger.error("Monitoring cycle completed with upload errors")
            else:
                logger.error("Monitoring cycle failed - image capture error")
                # Try to upload just the sensor data without image
                if mock_api.upload_data(sensor_data, None, use_real_api):
                    logger.info("Uploaded sensor data only (no image)")
        else:
            # Upload just sensor data without image
            if mock_api.upload_data(sensor_data, None, use_real_api):
                next_image = last_image_capture + IMAGE_CAPTURE_INTERVAL - current_time
                logger.info(f"Monitoring cycle completed successfully. "
                           f"Next image in {next_image:.1f} seconds")
            else:
                logger.error("Monitoring cycle completed with upload errors")
            
        return True
    
    except Exception as e:
        logger.error(f"Error during monitoring cycle: {str(e)}")
        return False


def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='Smart Fridge Simulator')
    
    parser.add_argument(
        '--interval', 
        type=int, 
        default=MONITORING_INTERVAL,
        help=f'Monitoring interval in seconds (default: {MONITORING_INTERVAL})'
    )
    
    parser.add_argument(
        '--image-interval', 
        type=int, 
        default=IMAGE_CAPTURE_INTERVAL,
        help=f'Image capture interval in seconds (default: {IMAGE_CAPTURE_INTERVAL})'
    )
    
    parser.add_argument(
        '--real-api', 
        action='store_true',
        help='Use real API endpoint instead of simulating'
    )
    
    return parser.parse_args()


def run():
    """Main run loop"""
    global use_real_api
    
    # Parse command line arguments
    args = parse_arguments()
    
    # Set global variables based on arguments
    monitoring_interval = args.interval
    image_interval = args.image_interval
    use_real_api = args.real_api
    
    if use_real_api:
        logger.info("Using real API endpoint for uploads")
    else:
        logger.info("Simulating API uploads")
    
    if not initialize():
        return 1
    
    try:
        # Schedule the monitoring function
        schedule.every(monitoring_interval).seconds.do(monitoring_cycle)
        
        # Run the first cycle immediately
        monitoring_cycle()
        
        # Main loop
        logger.info(f"Monitoring started with interval: {monitoring_interval} seconds")
        logger.info(f"Image capture interval: {image_interval} seconds")
        
        while running:
            schedule.run_pending()
            time.sleep(1)
        
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
    finally:
        cleanup()
    
    return 0


if __name__ == "__main__":
    logger.info("========== Smart Fridge Simulator Starting ==========")
    logger.info(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    sys.exit(run()) 