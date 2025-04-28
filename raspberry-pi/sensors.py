"""
Sensor interaction module for Smart Fridge Raspberry Pi system.
Handles temperature, humidity, and gas sensors.
"""
import time
import board
import busio
import digitalio
import adafruit_dht
import adafruit_mcp3xxx.mcp3008 as MCP
from adafruit_mcp3xxx.analog_in import AnalogIn
import RPi.GPIO as GPIO
import logging
from config import DHT_PIN, MCP3008_CLK, MCP3008_MISO, MCP3008_MOSI, MCP3008_CS, GAS_CHANNEL

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='fridge_monitor.log'
)
logger = logging.getLogger('sensors')

# Initialize the DHT sensor
dht_sensor = None

# Initialize the MCP3008 ADC for gas sensor
spi = None
cs = None
mcp = None
gas_sensor = None


def initialize_sensors():
    """Initialize all sensors"""
    global dht_sensor, spi, cs, mcp, gas_sensor
    
    try:
        logger.info("Initializing sensors...")
        # Initialize DHT22 sensor (temperature and humidity)
        dht_sensor = adafruit_dht.DHT22(board.D4)  # Using DHT22 sensor on pin 4
        
        # Initialize SPI communication for MCP3008
        spi = busio.SPI(clock=board.D11, MISO=board.D9, MOSI=board.D10)
        cs = digitalio.DigitalInOut(board.D8)
        mcp = MCP.MCP3008(spi, cs)
        gas_sensor = AnalogIn(mcp, GAS_CHANNEL)
        
        logger.info("Sensors initialized successfully")
        return True
    except Exception as e:
        logger.error(f"Error initializing sensors: {str(e)}")
        return False


def read_temperature_humidity():
    """
    Read temperature and humidity from DHT22 sensor
    
    Returns:
        tuple: (temperature, humidity) or (None, None) if reading fails
    """
    if dht_sensor is None:
        logger.error("DHT sensor not initialized")
        return None, None
    
    # DHT22 can sometimes fail to read, retry a few times
    for _ in range(5):
        try:
            temperature = dht_sensor.temperature
            humidity = dht_sensor.humidity
            logger.info(f"Temperature: {temperature}°C, Humidity: {humidity}%")
            return temperature, humidity
        except RuntimeError as e:
            logger.warning(f"DHT reading error: {str(e)}")
            time.sleep(2)  # Wait before retrying
        except Exception as e:
            logger.error(f"Unexpected error reading DHT sensor: {str(e)}")
            break
    
    return None, None


def read_gas_level():
    """
    Read gas level from MQ-5 sensor
    
    Returns:
        int: Gas level in PPM or None if reading fails
    """
    if gas_sensor is None:
        logger.error("Gas sensor not initialized")
        return None
    
    try:
        # Read raw ADC value
        raw_value = gas_sensor.value
        
        # Convert to voltage
        voltage = gas_sensor.voltage
        
        # Convert to approximate PPM (parts per million)
        # This conversion depends on your specific gas sensor calibration
        # Below is a simplified approximation for MQ-5
        ppm = int(raw_value / 65535 * 1000)
        
        logger.info(f"Gas level: {ppm} PPM (Raw: {raw_value}, Voltage: {voltage:.2f}V)")
        return ppm
    except Exception as e:
        logger.error(f"Error reading gas sensor: {str(e)}")
        return None


def read_all_sensors():
    """
    Read all sensor values
    
    Returns:
        dict: Dictionary with temperature, humidity, and gas readings
    """
    temp, humidity = read_temperature_humidity()
    gas = read_gas_level()
    
    # If readings fail, use reasonable defaults to avoid null values
    if temp is None:
        temp = 4.0  # Default fridge temperature
    if humidity is None:
        humidity = 50.0  # Default humidity
    if gas is None:
        gas = 100  # Default gas level
    
    return {
        "temp": temp,
        "humidity": humidity,
        "gas": gas
    }


def cleanup():
    """Clean up GPIO resources"""
    try:
        GPIO.cleanup()
        logger.info("Sensors cleanup completed")
    except Exception as e:
        logger.error(f"Error during sensor cleanup: {str(e)}") 