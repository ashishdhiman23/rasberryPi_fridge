# Smart Fridge Raspberry Pi System Overview

## System Components and Flow

```
+----------------+     +-----------------+     +---------------+
| Sensors Module |     | Camera Module   |     | Config Module |
| (sensors.py)   |     | (camera.py)     |     | (config.py)   |
+----------------+     +-----------------+     +---------------+
       |                       |                      |
       v                       v                      v
+--------------------------------------------------------------+
|                        Main Module                           |
|                        (main.py)                             |
+--------------------------------------------------------------+
                             |
                             v
                      +--------------+
                      | API Module   |
                      | (api.py)     |
                      +--------------+
                             |
                             v
                     +----------------+
                     | Backend Server |
                     +----------------+
```

## Module Responsibilities

### Main Module (main.py)
- Entry point for the Smart Fridge monitoring system
- Initializes sensors and camera modules
- Runs monitoring cycles at configured intervals
- Orchestrates data collection and API uploads
- Handles graceful shutdown and cleanup

### Sensors Module (sensors.py)
- Initializes and manages hardware sensors:
  - DHT22 for temperature and humidity
  - MQ-5 gas sensor (via MCP3008 ADC)
- Provides functions to read sensor data
- Handles sensor errors and retries

### Camera Module (camera.py)
- Initializes and manages PiCamera
- Captures images at configured intervals
- Processes and encodes images to base64 for API upload

### API Module (api.py)
- Handles communication with backend server
- Uploads sensor data and captured images
- Implements error handling and retry logic

### Config Module (config.py)
- Centralizes system configuration
- Defines hardware pin assignments
- Sets monitoring intervals and API endpoints

## Hardware Components
- Raspberry Pi (main controller)
- DHT22 temperature and humidity sensor
- MQ-5 gas sensor
- MCP3008 analog-to-digital converter
- Raspberry Pi Camera Module

## Data Flow
1. Sensors collect environmental data (temperature, humidity, gas levels)
2. Camera captures images of fridge interior
3. Main module aggregates all data
4. API module transmits data to backend server
5. Process repeats based on configured intervals

## Configuration Options
Configuration settings in config.py control:
- Monitoring frequency
- Image capture frequency
- Sensor pin assignments
- API endpoint URLs 