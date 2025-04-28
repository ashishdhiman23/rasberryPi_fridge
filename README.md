# Smart Fridge Raspberry Pi Monitoring System

This project is a comprehensive monitoring system for a smart refrigerator using Raspberry Pi. It includes both the Raspberry Pi code for hardware integration and a simulator for testing without physical hardware.

## Project Components

### Raspberry Pi Module
The Raspberry Pi module includes:
- Temperature and humidity monitoring
- Gas sensor for detecting refrigerant leaks
- Camera for capturing interior images
- API for uploading data to a backend server

### Simulator
The simulator allows testing without Raspberry Pi hardware:
- Generates realistic sensor readings
- Creates synthetic fridge interior images
- Uploads data to your backend API
- Simulates hardware failures to test robustness

## Getting Started

### Hardware Requirements
For the full Raspberry Pi implementation:
- Raspberry Pi (3B+ or 4 recommended)
- DHT22 temperature and humidity sensor
- MQ-5 gas sensor with MCP3008 ADC
- Raspberry Pi Camera Module
- Internet connectivity

### Testing with the Simulator
To test without hardware:

1. Install dependencies:
   ```
   cd simulator
   pip install -r requirements.txt
   ```

2. Configure the simulator:
   Edit the `.env` file to set your API endpoint:
   ```
   API_BASE_URL=http://your-api-server/api
   ```

3. Run the simulator:
   ```
   # On Windows:
   run_simulator.bat
   
   # On Linux/Mac:
   python run_simulator.py
   ```

4. Optional: Run the mock API server (if your backend is not available):
   ```
   # On Windows:
   run_mock_server.bat
   
   # On Linux/Mac:
   python -m simulator.mock_server
   ```

## Command-line Options

The simulator supports various options:
```
python run_simulator.py --interval 10 --image-interval 60 --real-api
```

- `--interval`: Seconds between sensor readings (default: 30)
- `--image-interval`: Seconds between image captures (default: 300)
- `--real-api`: Use real API endpoint instead of simulation

## Development

### Project Structure
```
├── raspberry-pi/       # Raspberry Pi code (for hardware)
│   ├── main.py         # Main entry point
│   ├── sensors.py      # Sensor interaction
│   ├── camera.py       # Camera management
│   ├── api.py          # API communication
│   └── config.py       # Configuration
│
├── simulator/          # Simulator code (no hardware needed)
│   ├── simulator.py    # Main simulator
│   ├── mock_sensors.py # Sensor simulation
│   ├── mock_camera.py  # Camera simulation
│   ├── mock_api.py     # API simulation
│   ├── mock_server.py  # Mock backend server
│   └── config.py       # Simulator configuration
│
├── run_simulator.py    # Wrapper to run simulator
├── run_simulator.bat   # Windows batch for simulator
└── run_mock_server.bat # Windows batch for mock server
```

## Contributing
Contributions are welcome! Please feel free to submit a Pull Request.

## License
This project is licensed under the MIT License - see the LICENSE file for details. 