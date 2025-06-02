# Smart Fridge Raspberry Pi Hardware Setup Guide

This guide provides step-by-step instructions for setting up the Raspberry Pi-based Smart Fridge monitoring system.

## Hardware Requirements

- Raspberry Pi 4 (2GB+ RAM recommended)
- DHT22 temperature and humidity sensor
- MQ-2 gas sensor
- Raspberry Pi Camera Module V2 or compatible
- microSD card (16GB+ recommended)
- Power supply for Raspberry Pi
- Breadboard and jumper wires
- Optional: Case for Raspberry Pi

## Hardware Assembly

### Step 1: Prepare the Raspberry Pi

1. Install Raspberry Pi OS using the Raspberry Pi Imager tool ([download here](https://www.raspberrypi.org/software/))
2. During setup, enable SSH and configure WiFi if needed
3. Insert the microSD card into the Raspberry Pi and connect the power supply

### Step 2: Connect the DHT22 Temperature/Humidity Sensor

1. Connect the DHT22 sensor to the Raspberry Pi:
   - VCC pin to 3.3V (Pin 1)
   - GND pin to Ground (Pin 6)
   - DATA pin to GPIO4 (Pin 7)
   - Use a 10kΩ resistor between VCC and DATA pins

```
DHT22      Raspberry Pi
-----------------------
VCC   -->  3.3V (Pin 1)
DATA  -->  GPIO4 (Pin 7)
GND   -->  Ground (Pin 6)
```

### Step 3: Connect the MQ-2 Gas Sensor

1. Connect the MQ-2 gas sensor to the Raspberry Pi:
   - VCC pin to 5V (Pin 2)
   - GND pin to Ground (Pin 9)
   - AOUT pin to MCP3008 ADC (see note below)
   - DOUT pin to GPIO17 (Pin 11)

```
MQ-2       Raspberry Pi
-----------------------
VCC   -->  5V (Pin 2)
GND   -->  Ground (Pin 9)
DOUT  -->  GPIO17 (Pin 11)
```

**Note**: Since Raspberry Pi doesn't have analog inputs, you'll need an MCP3008 ADC (Analog-to-Digital Converter) to read analog values from the AOUT pin of the MQ-2 sensor. The configuration for MCP3008 requires additional connections:

```
MCP3008    Raspberry Pi
-----------------------
VDD   -->  3.3V (Pin 1)
VREF  -->  3.3V (Pin 1)
AGND  -->  Ground (Pin 6)
CLK   -->  GPIO11/SCLK (Pin 23)
DOUT  -->  GPIO9/MISO (Pin 21)
DIN   -->  GPIO10/MOSI (Pin 19)
CS    -->  GPIO8/CE0 (Pin 24)
DGND  -->  Ground (Pin 6)
```

Then connect:
```
MQ-2       MCP3008
-----------------------
AOUT  -->  CH0 (Channel 0)
```

### Step 4: Connect the Camera Module

1. Locate the Camera Serial Interface (CSI) connector on the Raspberry Pi
2. Gently pull up the plastic clip on the CSI connector
3. Insert the camera ribbon cable with the blue side facing the USB ports
4. Push down the plastic clip to secure the cable

### Step 5: Final Assembly

1. Double-check all connections
2. Consider mounting the components in a case for protection
3. Position the camera module for a clear view of the fridge interior
4. Secure sensors inside the fridge, ensuring wires can safely reach the Raspberry Pi

## Software Installation

### Step 1: Update the System

```bash
sudo apt update
sudo apt upgrade -y
```

### Step 2: Enable Camera Interface

```bash
sudo raspi-config
```

Navigate to `Interface Options` > `Camera` and select `Yes` to enable the camera interface. Reboot when prompted.

### Step 3: Install Required Packages

```bash
sudo apt install -y python3-pip python3-dev
sudo apt install -y python3-picamera
sudo pip3 install adafruit-circuitpython-dht
sudo apt install -y libgpiod2
```

For the MQ-2 sensor with MCP3008:
```bash
sudo pip3 install adafruit-blinka
sudo pip3 install adafruit-circuitpython-mcp3xxx
```

### Step 4: Clone the Repository

```bash
git clone https://github.com/your-org/smart-fridge.git
cd smart-fridge
```

### Step 5: Install Python Dependencies

```bash
pip3 install -r requirements.txt
```

## Configuration

Edit the `config.py` file to match your hardware setup:

```python
# Sensor Pins (BCM numbering)
DHT_PIN = 4
GAS_PIN = 17
MCP3008_CHANNEL = 0

# Camera Settings
CAMERA_RESOLUTION = (1920, 1080)
CAMERA_ROTATION = 0
CAMERA_FRAMERATE = 15

# API Settings
API_BASE_URL = "https://smart-fridge-backend.onrender.com/api"
UPLOAD_ENDPOINT = f"{API_BASE_URL}/upload/multipart"
MAX_UPLOAD_RETRIES = 3
UPLOAD_RETRY_DELAY = 5  # seconds

# Monitoring Settings
MONITORING_INTERVAL = 300  # seconds (5 minutes)
```

Adjust the pin numbers and settings as needed based on your specific hardware configuration.

## Testing the Hardware

### Test the DHT22 Sensor

Create a test script called `test_dht.py`:

```python
import time
import board
import adafruit_dht

# Initialize the DHT device
dht = adafruit_dht.DHT22(board.D4)  # D4 = GPIO4

while True:
    try:
        # Print the values to the serial port
        temperature = dht.temperature
        humidity = dht.humidity
        print(f"Temperature: {temperature:.1f}°C, Humidity: {humidity:.1f}%")
    except RuntimeError as e:
        # Reading doesn't always work, just continue
        print(f"Reading error: {e}")
    
    time.sleep(2)
```

Run it with:
```bash
python3 test_dht.py
```

### Test the MQ-2 Sensor

Create a test script called `test_mq2.py`:

```python
import time
import board
import busio
import digitalio
import adafruit_mcp3xxx.mcp3008 as MCP
from adafruit_mcp3xxx.analog_in import AnalogIn

# Create the SPI bus
spi = busio.SPI(clock=board.SCK, MISO=board.MISO, MOSI=board.MOSI)

# Create the CS (Chip Select)
cs = digitalio.DigitalInOut(board.D8)  # D8 = GPIO8/CE0

# Create the MCP3008 object
mcp = MCP.MCP3008(spi, cs)

# Create an analog input channel on pin 0
chan = AnalogIn(mcp, MCP.P0)

while True:
    print(f"Raw ADC Value: {chan.value}")
    print(f"ADC Voltage: {chan.voltage:.2f}V")
    
    # Calculate gas level (this is a simplified approximation)
    gas_level = chan.value / 65535 * 100
    print(f"Gas Level: {gas_level:.1f}%")
    
    time.sleep(0.5)
```

Run it with:
```bash
python3 test_mq2.py
```

### Test the Camera

Create a test script called `test_camera.py`:

```python
from picamera import PiCamera
from time import sleep

# Initialize the camera
camera = PiCamera()
camera.resolution = (1920, 1080)
camera.rotation = 0  # Adjust if needed

# Start preview (requires a display attached to the Raspberry Pi)
camera.start_preview(alpha=200)  # Alpha makes it slightly transparent

# Wait to allow the camera to adjust to lighting conditions
print("Adjusting to light conditions...")
sleep(5)

# Capture an image
print("Capturing image...")
camera.capture('test_image.jpg')
print("Image saved as test_image.jpg")

# Stop preview
camera.stop_preview()
camera.close()
```

Run it with:
```bash
python3 test_camera.py
```

## Running the System

To start the Smart Fridge monitoring system:

```bash
python3 main.py
```

For debugging:

```bash
python3 main.py --debug
```

### Setting Up Autostart

To make the system start automatically when the Raspberry Pi boots:

1. Edit the crontab:
```bash
crontab -e
```

2. Add the following line:
```
@reboot cd /path/to/smart-fridge && python3 main.py >> /home/pi/smart_fridge.log 2>&1
```

3. Save and exit

## Troubleshooting

### Common Issues

#### DHT22 Sensor Reading Errors

If you get frequent reading errors:
- Check wiring connections
- Ensure the correct GPIO pin is configured
- Try adding a 10kΩ pull-up resistor if not already present
- Make sure you're using the latest Adafruit DHT library

#### Camera Not Working

If the camera isn't working:
- Check that the ribbon cable is properly connected
- Ensure the camera is enabled in `raspi-config`
- Verify that the camera ribbon cable is not damaged
- Try a different camera module if available

#### MQ-2 Sensor Issues

If the gas sensor isn't providing readings:
- Allow a warm-up period (24 hours for first use, 1-2 minutes for subsequent uses)
- Check ADC connections
- Verify the correct channel is configured in the code
- Test with direct GPIO connection for digital readings

#### Upload Failures

If data isn't uploading to the backend:
- Check internet connectivity
- Verify API URL configuration
- Ensure the backend server is running
- Check firewall settings

## Maintenance

### Regular Checks

1. Clean camera lens periodically with a soft cloth
2. Check sensor connections monthly
3. Ensure good ventilation around the MQ-2 sensor
4. Monitor system logs for any errors or unusual readings

### Updating the System

```bash
cd /path/to/smart-fridge
git pull
pip3 install -r requirements.txt
```

## Safety Considerations

- Ensure all electrical connections are properly insulated
- Keep the Raspberry Pi and sensors away from water or excessive moisture
- The MQ-2 sensor can get warm during operation - this is normal
- Ensure the system is protected from physical damage inside the refrigerator

## Next Steps

After setting up the hardware:

1. Explore the [API Reference](./api_reference.md) for details on data transmission
2. Check the [API Integration Guide](./api_integration_guide.md) for integrating with mobile applications
3. Set up the simulator for development by following the [Simulator Setup Guide](./setup_simulator.md) 