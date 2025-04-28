#!/usr/bin/env python3
"""
Main entry point for Smart Fridge Raspberry Pi monitoring system.
Initializes sensors and camera, then periodically reads data and uploads to API.
"""
import time
import signal
import sys
import logging
import schedule
from datetime import datetime

# Import modules
import sensors
import camera
import api
from config import MONITORING_INTERVAL, IMAGE_CAPTURE_INTERVAL

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='fridge_monitor.log',
    filemode='a'
)
logger = logging.getLogger('main')

# Control variables
running = True
last_image_capture = 0


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
    
    # Initialize sensors and camera
    if not sensors.initialize_sensors():
        logger.error("Failed to initialize sensors, exiting...")
        return False
    
    if not camera.initialize_camera():
        logger.error("Failed to initialize camera, exiting...")
        sensors.cleanup()
        return False
    
    logger.info("System initialized successfully")
    return True


def cleanup():
    """Clean up resources before exiting"""
    logger.info("Cleaning up resources...")
    sensors.cleanup()
    camera.cleanup()
    logger.info("Cleanup complete, exiting...")


def monitor_cycle():
    """Run a complete monitoring cycle"""
    global last_image_capture
    
    try:
        current_time = time.time()
        logger.info("Starting monitoring cycle...")
        
        # Read sensor data
        sensor_data = sensors.read_all_sensors()
        
        # Decide if we need to capture an image
        capture_now = current_time - last_image_capture >= IMAGE_CAPTURE_INTERVAL
        
        if capture_now:
            # Capture image
            image_base64 = camera.capture_image()
            
            if image_base64:
                # Update last capture time
                last_image_capture = current_time
                
                # Upload data to API
                if api.upload_data(sensor_data, image_base64):
                    logger.info("Monitoring cycle completed successfully")
                else:
                    logger.error("Monitoring cycle completed with upload errors")
            else:
                logger.error("Monitoring cycle failed - image capture error")
        else:
            next_capture = last_image_capture + IMAGE_CAPTURE_INTERVAL - current_time
            logger.info(f"Skipping image capture, next capture in {next_capture:.1f} seconds")
            
        return True
    
    except Exception as e:
        logger.error(f"Error during monitoring cycle: {str(e)}")
        return False


def run():
    """Main run loop"""
    if not initialize():
        return 1
    
    try:
        # Schedule the monitoring function
        schedule.every(MONITORING_INTERVAL).seconds.do(monitor_cycle)
        
        # Run the first cycle immediately
        monitor_cycle()
        
        # Main loop
        logger.info(f"Monitoring started with interval: {MONITORING_INTERVAL} seconds")
        while running:
            schedule.run_pending()
            time.sleep(1)
        
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
    finally:
        cleanup()
    
    return 0


if __name__ == "__main__":
    logger.info("========== Smart Fridge Monitor Starting ==========")
    logger.info(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    sys.exit(run()) 