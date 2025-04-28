# Smart Fridge Simulator

A simulation environment for testing the Smart Fridge monitoring system without requiring Raspberry Pi hardware. The simulator generates realistic sensor readings and synthetic fridge images that can be used to test the backend API and frontend visualization.

## Features

- Simulates temperature, humidity, and gas sensor readings
- Generates synthetic refrigerator interior images
- Supports both mock API uploads and real API endpoint integration
- Configurable monitoring and image capture intervals
- Random variation and occasional simulated failures to test error handling

## Installation

1. Create a virtual environment (recommended):
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Optional: Create a `.env` file in the project root to configure environment variables:
   ```
   API_BASE_URL=http://your-api-server/api
   ```

## Usage

To run the simulator with default settings:

```
python simulator.py
```

### Command-line Options

The simulator supports the following command-line arguments:

- `--interval SECONDS`: Set the monitoring interval (default: 30 seconds)
- `--image-interval SECONDS`: Set the image capture interval (default: 300 seconds)
- `--real-api`: Use real API endpoint instead of simulating uploads

Example:
```
python simulator.py --interval 10 --image-interval 60 --real-api
```

## Output

- Sensor readings and image data are logged to `simulator.log`
- Mock images are saved to the `simulator/mock_images/` directory
- The most recent mock upload data is saved to `simulator/last_upload.json`

## Integration with Backend

To test with your actual backend API:

1. Set the `API_BASE_URL` in the `.env` file or in `config.py`
2. Run the simulator with the `--real-api` flag:
   ```
   python simulator.py --real-api
   ```

## Customization

You can customize the simulator's behavior by modifying the parameters in `config.py`:

- Sensor value ranges
- Image generation settings
- API endpoints
- Monitoring intervals 