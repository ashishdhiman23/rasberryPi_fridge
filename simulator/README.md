# Smart Fridge Simulator

A simulation environment for testing the Smart Fridge monitoring system without requiring Raspberry Pi hardware. The simulator generates realistic sensor readings and synthetic fridge images that can be used to test the backend API and frontend visualization.

## Features

- Simulates temperature, humidity, and gas sensor readings with configurable ranges
- Generates synthetic refrigerator interior images with recognizable food items
- Supports both simulated API responses and real API endpoint integration
- Configurable monitoring and image capture intervals via command-line options
- Random variation and occasional simulated failures to test error handling
- Supports custom fridge images for more realistic testing
- Logs detailed operation information for debugging

## System Architecture

The simulator consists of the following components:

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

### Component Descriptions

1. **simulator.py**: The main module that orchestrates the simulation, including:
   - Scheduling monitoring cycles
   - Reading sensor data
   - Capturing images
   - Uploading data to API
   - Processing command-line arguments

2. **mock_sensors.py**: Simulates hardware sensors with realistic readings:
   - Temperature and humidity readings
   - Gas level readings
   - Occasional sensor failures

3. **mock_camera.py**: Generates synthetic fridge images or uses custom images:
   - Creates images with recognizable food items
   - Applies realistic visual effects
   - Handles custom image selection

4. **mock_api.py**: Handles API communication:
   - Simulates upload success/failure
   - Implements retry logic
   - Can connect to real backend API endpoints

5. **mock_server.py**: A simple Flask server that can be used for full testing:
   - Provides API endpoints for data reception
   - Stores received data and images
   - Returns appropriate responses

## Installation

1. Create a virtual environment (recommended):
   ```
   python -m venv .venv
   # On Linux/macOS:
   source .venv/bin/activate
   # On Windows PowerShell:
   .\.venv\Scripts\Activate.ps1
   # On Windows Command Prompt:
   .\.venv\Scripts\activate.bat
   ```

2. Install dependencies:
   ```
   pip install -r simulator/requirements.txt
   ```

3. Optional: Create a `.env` file in the project root to configure environment variables:
   ```
   API_BASE_URL=https://your-api-server.com/api
   ```

## Required Dependencies

The simulator requires the following Python packages:
- requests==2.28.1 - For API communication
- python-dotenv==0.21.0 - For loading environment variables
- schedule==1.1.0 - For scheduling monitoring cycles
- flask==2.2.2 - For the mock server
- pillow==9.3.0 - For image processing
- numpy==1.23.5 - For numerical operations

## Usage

There are two ways to run the simulator:

### 1. Using the run_simulator.py wrapper script

To run the simulator from the project root directory:

```
python run_simulator.py [options]
```

### 2. Running simulator.py directly

If you're inside the simulator directory:

```
python simulator.py [options]
```

### Command-line Options

The simulator supports the following command-line arguments:

- `--interval SECONDS`: Set the monitoring interval (default: 30 seconds)
- `--image-interval SECONDS`: Set the image capture interval (default: 300 seconds)
- `--real-api`: Use real API endpoint instead of simulating uploads

Example:
```
python run_simulator.py --interval 30 --image-interval 60 --real-api
```

## Output

- Detailed logs are written to `simulator.log`
- Mock images are saved to the `simulator/mock_images/` directory
- The most recent API response is saved to `simulator/last_api_response.json`
- The last upload data is saved to `simulator/last_upload.json`

## Using Custom Images

You can add your own refrigerator images to be used by the simulator:

1. Place your custom images in the `simulator/mock_images/` directory
2. Ensure the image filenames do NOT start with `fridge_` (this prefix is used for generated images)
3. Supported formats: `.jpg`, `.jpeg`, `.png`

When custom images are present, the simulator will randomly select one of your images instead of generating synthetic ones. If no custom images are found, it falls back to generating synthetic images.

Example:
```
simulator/mock_images/my_fridge1.jpg
simulator/mock_images/refrigerator_photo.png
```

## Integration with Backend

To test with your actual backend API:

1. Set the `UPLOAD_ENDPOINT` in the `simulator/config.py` file or use the `.env` file
2. Run the simulator with the `--real-api` flag:
   ```
   python run_simulator.py --real-api
   ```

The simulator will attempt to upload data to the specified API endpoint using multipart/form-data format. If API calls fail, the simulator will automatically retry according to the configuration settings.

## Running the Mock Server

The mock server provides a simple API endpoint for testing:

```
python simulator/mock_server.py
```

This will start a Flask server on http://localhost:5000 with the following endpoints:
- `/api/upload` - For receiving sensor data and images
- `/api/status` - For checking server status

## Customization

You can customize the simulator's behavior by modifying the parameters in `simulator/config.py`:

### API Settings
- `UPLOAD_ENDPOINT` - The URL to upload data to
- `MAX_UPLOAD_RETRIES` - Number of retry attempts for failed uploads
- `UPLOAD_RETRY_DELAY` - Seconds to wait between retry attempts

### Sensor Settings
- `DEFAULT_TEMP` - Default temperature in °C
- `DEFAULT_HUMIDITY` - Default humidity in %
- `DEFAULT_GAS` - Default gas level in PPM
- `TEMP_MIN` and `TEMP_MAX` - Temperature range
- `HUMIDITY_MIN` and `HUMIDITY_MAX` - Humidity range
- `GAS_MIN` and `GAS_MAX` - Gas level range

### Camera Settings
- `MOCK_IMAGE_WIDTH` and `MOCK_IMAGE_HEIGHT` - Image dimensions
- `MOCK_IMAGE_PATH` - Directory for storing images

### Monitoring Settings
- `MONITORING_INTERVAL` - Seconds between sensor readings
- `IMAGE_CAPTURE_INTERVAL` - Seconds between image captures

## Troubleshooting

### Common Issues

1. **Module not found errors**:
   - Ensure all dependencies are installed: `pip install -r simulator/requirements.txt`
   - If running directly, make sure you're in the right directory

2. **API connection errors**:
   - Check if the API endpoint in `config.py` is correct
   - Ensure the server is running and accessible
   - Look at `simulator.log` for detailed error messages

3. **Image generation issues**:
   - Check if the PIL (Pillow) library is installed correctly
   - Ensure the `simulator/mock_images` directory exists and is writable

4. **Bad Gateway or 404 errors**:
   - The backend service might be unavailable or still starting up
   - Check if your API URL is correct
   - The endpoint may have changed path or parameters

## Development and Extending

To extend the simulator for your needs:

1. Add new mock sensors in `mock_sensors.py`
2. Modify the image generation in `mock_camera.py`
3. Enhance the API handling in `mock_api.py`
4. Add new command-line options in `simulator.py`

All components are designed to be modular and easily extendable. 