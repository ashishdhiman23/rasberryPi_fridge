"""
Mock sensor module for Smart Fridge Simulator.
Generates realistic sensor readings without actual hardware.
"""
import random
import logging
from simulator.config import (
    DEFAULT_TEMP, DEFAULT_HUMIDITY, DEFAULT_GAS,
    TEMP_MIN, TEMP_MAX, HUMIDITY_MIN, HUMIDITY_MAX, GAS_MIN, GAS_MAX
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='simulator.log'
)
logger = logging.getLogger('mock_sensors')


def initialize_sensors():
    """Mock initialization of sensors"""
    logger.info("Initializing mock sensors...")
    # No actual hardware to initialize, just log the action
    logger.info("Mock sensors initialized successfully")
    return True


def read_temperature_humidity():
    """
    Generate mock temperature and humidity values
    
    Returns:
        tuple: (temperature, humidity)
    """
    # Generate realistic values with some random variation
    temperature = round(random.uniform(TEMP_MIN, TEMP_MAX), 1)
    humidity = round(random.uniform(HUMIDITY_MIN, HUMIDITY_MAX), 1)
    
    logger.info(f"Mock Temperature: {temperature}°C, Humidity: {humidity}%")
    return temperature, humidity


def read_gas_level():
    """
    Generate mock gas level values
    
    Returns:
        int: Gas level in PPM
    """
    # Generate realistic gas level with some random variation
    gas_level = int(random.uniform(GAS_MIN, GAS_MAX))
    
    logger.info(f"Mock Gas level: {gas_level} PPM")
    return gas_level


def read_all_sensors():
    """
    Read all mock sensor values
    
    Returns:
        dict: Dictionary with temperature, humidity, and gas readings
    """
    temp, humidity = read_temperature_humidity()
    gas = read_gas_level()
    
    # Randomly simulate sensor failures (10% chance)
    if random.random() < 0.1:
        logger.warning("Simulating occasional sensor read failure")
        if random.choice([True, False]):
            temp = None
        if random.choice([True, False]):
            humidity = None
        if random.choice([True, False]):
            gas = None
    
    # If readings fail, use reasonable defaults to avoid null values
    if temp is None:
        temp = DEFAULT_TEMP
    if humidity is None:
        humidity = DEFAULT_HUMIDITY
    if gas is None:
        gas = DEFAULT_GAS
    
    return {
        "temp": temp,
        "humidity": humidity,
        "gas": gas
    }


def cleanup():
    """Mock cleanup of sensors"""
    logger.info("Mock sensors cleanup completed")
    return True 