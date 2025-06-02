# Smart Fridge Simulator Setup Guide

This guide provides step-by-step instructions for setting up and running the Smart Fridge Simulator for development and testing.

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Git (for version control)

## Installation Steps

### 1. Clone the Repository

```bash
git clone https://github.com/your-org/smart-fridge.git
cd smart-fridge
```

### 2. Set Up a Virtual Environment

#### On Windows:
```bash
python -m venv venv
venv\Scripts\activate
```

#### On macOS/Linux:
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

Navigate to the simulator directory:
```bash
cd simulator
pip install -r requirements.txt
```

## Configuration

Before running the simulator, you may want to customize its behavior. The configuration is stored in `simulator/config.py`.

### Key Configuration Options

- `API_BASE_URL`: The backend API URL where data will be sent
- `UPLOAD_ENDPOINT`: The specific endpoint for data upload
- `MOCK_SENSORS_ENABLED`: Enable/disable mock sensor data generation
- `MOCK_CAMERA_ENABLED`: Enable/disable mock camera functionality
- `TEMP_MIN` and `TEMP_MAX`: Range for simulated temperature values
- `HUMIDITY_MIN` and `HUMIDITY_MAX`: Range for simulated humidity values
- `MONITORING_INTERVAL`: How often to collect and send data (in seconds)

### Example Configuration

```python
# API Settings
API_BASE_URL = "https://smart-fridge-backend.onrender.com/api"
UPLOAD_ENDPOINT = f"{API_BASE_URL}/upload/multipart"
MAX_UPLOAD_RETRIES = 3
UPLOAD_RETRY_DELAY = 5  # seconds

# Mock Sensors Settings
MOCK_SENSORS_ENABLED = True
TEMP_MIN = 2.0
TEMP_MAX = 8.0
TEMP_VARIATION = 0.5
HUMIDITY_MIN = 30.0
HUMIDITY_MAX = 70.0
HUMIDITY_VARIATION = 2.0
GAS_BASE_VALUE = 50
GAS_VARIATION = 10

# Mock Camera Settings
MOCK_CAMERA_ENABLED = True
MOCK_IMAGE_PATH = "simulator/mock_images"
CUSTOM_IMAGES_ENABLED = True

# Monitoring Settings
MONITORING_INTERVAL = 300  # seconds (5 minutes)
```

## Running the Simulator

To start the simulator:

```bash
python simulator.py
```

### Command Line Options

The simulator supports several command line options:

- `--debug`: Enable debug logging for more detailed output
- `--interval=N`: Override the monitoring interval to N seconds
- `--no-camera`: Disable the mock camera functionality
- `--no-sensors`: Disable the mock sensor functionality
- `--api-url=URL`: Override the API base URL

Example:
```bash
python simulator.py --debug --interval=60 --api-url=http://localhost:5000/api
```

## Simulator Components

The simulator consists of several key components:

### 1. Mock Sensors (`mock_sensors.py`)

Generates simulated temperature, humidity, and gas level readings with random variations to mimic real sensor behavior.

### 2. Mock Camera (`mock_camera.py`)

Provides simulated fridge interior images. It can either:
- Generate synthetic images of a refrigerator interior with random food items
- Use pre-existing images from the `mock_images` directory

### 3. Mock API (`mock_api.py`)

Handles communication with the backend API, including:
- Formatting sensor data and images for upload
- Simulating network conditions (success, failure, latency)
- Retrying failed uploads

### 4. Main Simulator (`simulator.py`)

Coordinates all components, schedules monitoring cycles, and handles graceful shutdown.

## Monitoring the Simulator

The simulator creates log files in the project directory:

- `simulator.log`: Contains information about simulator operation, including startup, monitoring cycles, and errors
- `last_upload.json`: Contains the last data payload sent to the API
- `last_api_response.json`: Contains the most recent API response

These files can be useful for debugging and verifying the simulator's behavior.

## Simulating Different Conditions

### Temperature Changes

To simulate different temperature conditions, modify `TEMP_MIN` and `TEMP_MAX` in `config.py`.

For a cold fridge:
```python
TEMP_MIN = 1.0
TEMP_MAX = 3.0
```

For a warmer fridge (potential problem):
```python
TEMP_MIN = 6.0
TEMP_MAX = 12.0
```

### Network Issues

The mock API includes functionality to simulate network issues. To adjust:

1. Open `mock_api.py`
2. Modify the `simulate_upload` function:

```python
def simulate_upload(data, image_data):
    """Simulate uploading data to the backend API."""
    # Simulate network conditions
    success_rate = 0.9  # 90% success rate
    latency = random.uniform(0.1, 2.0)  # 0.1 to 2.0 seconds latency
    
    time.sleep(latency)  # Simulate network latency
    
    if random.random() > success_rate:
        logger.warning("Simulated network failure")
        return False, "Simulated network failure"
    
    logger.info(f"Successfully simulated upload with {latency:.2f}s latency")
    return True, "Success"
```

## Troubleshooting

### Common Issues

#### 1. ImportError when running simulator

```
ImportError: No module named 'requests'
```

**Solution**: Ensure you have activated the virtual environment and installed all dependencies:
```bash
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

#### 2. Permission denied when running simulator

```
Permission denied: 'simulator.py'
```

**Solution**: Make the file executable:
```bash
chmod +x simulator.py
```

#### 3. No images are being generated

**Solution**: Check that `MOCK_CAMERA_ENABLED` is set to `True` in `config.py` and ensure the `MOCK_IMAGE_PATH` directory exists.

#### 4. Simulator stops unexpectedly

**Solution**: Check the `simulator.log` file for any error messages. Common issues include:
- Network connectivity problems
- Permission issues writing to log files
- Memory or resource constraints

## Contributing to the Simulator

When modifying the simulator:

1. Create a new branch for your changes
2. Update tests to reflect your changes
3. Update documentation (including this setup guide if necessary)
4. Submit a pull request with a clear description of your changes

## Using Simulator Data in Development

The simulator is designed to provide realistic data for developing and testing the Smart Fridge application. You can:

- Use the simulator's API endpoints for mobile app development
- Analyze simulator data patterns to improve AI models
- Test system behavior under various conditions by adjusting the simulator configuration

## Next Steps

After setting up the simulator, you might want to:

1. Explore the [API Reference](./api_reference.md) for details on the API endpoints
2. Check the [API Integration Guide](./api_integration_guide.md) for help integrating with mobile applications
3. Set up the real Raspberry Pi system by following the [Hardware Setup Guide](./hardware_setup.md) 