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

## Simulator Overview

For development and testing without actual Raspberry Pi hardware, a simulator is provided that emulates the hardware components and data flow.

### Simulator Architecture

```
+----------------+     +-----------------+     +---------------+
| Mock Sensors   |     | Mock Camera     |     | Config Module |
| (mock_sensors) |     | (mock_camera)   |     | (config.py)   |
+----------------+     +-----------------+     +---------------+
       |                       |                      |
       v                       v                      v
+--------------------------------------------------------------+
|                     Simulator Module                         |
|                     (simulator.py)                           |
+--------------------------------------------------------------+
                             |
                             v
                      +--------------+
                      | Mock API     |
                      | (mock_api)   |
                      +--------------+
                             |
                             v
                     +----------------+
                     | Backend Server |
                     | (Real API or   |
                     | Mock Server)   |
                     +----------------+
```

### Simulator Components

1. **Simulator Module (simulator.py)**
   - Replaces the main.py module for simulation
   - Orchestrates mock sensors and camera
   - Schedules monitoring cycles
   - Handles command-line arguments for configuration

2. **Mock Sensors Module (mock_sensors.py)**
   - Generates realistic sensor readings without hardware
   - Simulates occasional sensor failures
   - Configurable temperature, humidity, and gas level ranges

3. **Mock Camera Module (mock_camera.py)**
   - Generates synthetic fridge interior images
   - Can use custom images for more realistic testing
   - Applies timestamps and visual effects

4. **Mock API Module (mock_api.py)**
   - Simulates API communication or connects to real backend
   - Implements retry logic and error handling
   - Provides detailed logging of API interactions

5. **Mock Server (mock_server.py)**
   - Optional Flask server for complete end-to-end testing
   - Provides API endpoints for receiving data
   - Stores received data and images

### Running the Simulator

The simulator can be run using the wrapper script:

```
python run_simulator.py --interval 30 --image-interval 60 [--real-api]
```

For more details on the simulator, refer to the [Simulator README](simulator/README.md). 