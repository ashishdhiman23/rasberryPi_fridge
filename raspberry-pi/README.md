# Smart Fridge Raspberry Pi Monitor

This component runs on a Raspberry Pi connected to temperature, humidity, and gas sensors, along with a camera to monitor your smart fridge's interior.

## Hardware Requirements

- Raspberry Pi (3 or newer recommended)
- DHT22 temperature and humidity sensor
- MQ-5 gas sensor (or similar)
- MCP3008 analog-to-digital converter
- Raspberry Pi Camera Module
- Jumper wires and breadboard

## Wiring Diagram

### DHT22 Temperature/Humidity Sensor
- Connect VCC to Raspberry Pi 3.3V
- Connect GND to Raspberry Pi GND
- Connect DATA to Raspberry Pi GPIO4

### MCP3008 ADC
- Connect VDD to Raspberry Pi 3.3V
- Connect VREF to Raspberry Pi 3.3V
- Connect AGND to Raspberry Pi GND
- Connect DGND to Raspberry Pi GND
- Connect CLK to Raspberry Pi GPIO11 (SCLK)
- Connect DOUT to Raspberry Pi GPIO9 (MISO)
- Connect DIN to Raspberry Pi GPIO10 (MOSI)
- Connect CS to Raspberry Pi GPIO8 (CE0)

### MQ-5 Gas Sensor
- Connect VCC to Raspberry Pi 5V
- Connect GND to Raspberry Pi GND
- Connect AO (Analog Output) to MCP3008 CH0

### Camera Module
- Connect the camera module to the Raspberry Pi's camera port

## Setup Instructions

1. Install system dependencies:
   ```bash
   sudo apt-get update
   sudo apt-get install -y python3-pip python3-dev python3-picamera
   sudo apt-get install -y libgpiod2 libatlas-base-dev
   ```

2. Clone the repository:
   ```bash
   git clone https://github.com/ashishdhiman23/rasberryPi_fridge.git
   cd rasberryPi_fridge/raspberry-pi
   ```

3. Install Python dependencies:
   ```bash
   pip3 install -r requirements.txt
   ```

4. Create configuration file:
   ```bash
   cp .env.example .env
   ```

5. Edit the .env file with your API endpoint:
   ```bash
   nano .env
   ```

## Running the Monitor

Start the monitoring service:
```bash
python3 main.py
```

For automatic startup on boot:

1. Create a systemd service:
   ```bash
   sudo nano /etc/systemd/system/fridge-monitor.service
   ```

2. Add the following content:
   ```
   [Unit]
   Description=Smart Fridge Monitor
   After=network.target

   [Service]
   User=pi
   WorkingDirectory=/home/pi/rasberryPi_fridge/raspberry-pi
   ExecStart=/usr/bin/python3 /home/pi/rasberryPi_fridge/raspberry-pi/main.py
   Restart=always
   RestartSec=10

   [Install]
   WantedBy=multi-user.target
   ```

3. Enable and start the service:
   ```bash
   sudo systemctl enable fridge-monitor.service
   sudo systemctl start fridge-monitor.service
   ```

4. Check status:
   ```bash
   sudo systemctl status fridge-monitor.service
   ```

## Troubleshooting

Check the log file for any errors:
```bash
tail -f fridge_monitor.log
```

## Configuration

You can adjust settings in the `config.py` file:
- Sensor pins
- Camera settings
- Monitoring intervals
- API endpoints 