#!/usr/bin/env python3
"""
Simple mock API server for testing the Smart Fridge Simulator.
Provides endpoints to receive sensor data and images.
"""
import os
import json
import base64
import logging
from datetime import datetime
from flask import Flask, request, jsonify

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='mock_server.log',
    filemode='a'
)
console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)

logger = logging.getLogger('mock_server')

# Create the Flask app
app = Flask(__name__)

# Create directories for storing received data
os.makedirs('mock_server_data', exist_ok=True)
os.makedirs('mock_server_data/images', exist_ok=True)


@app.route('/api/upload', methods=['POST'])
def upload():
    """Handle sensor data and image uploads"""
    try:
        # Get data from request
        data = request.json
        
        # Log the received data
        logger.info(f"Received upload with temperature: {data.get('temperature')}°C, "
                   f"humidity: {data.get('humidity')}%, "
                   f"gas: {data.get('gas_level')} PPM")
        
        # Generate timestamp for filenames
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save sensor data to JSON file
        sensor_data = {
            'timestamp': data.get('timestamp', timestamp),
            'temperature': data.get('temperature'),
            'humidity': data.get('humidity'),
            'gas_level': data.get('gas_level')
        }
        
        with open(f'mock_server_data/sensor_data_{timestamp}.json', 'w') as f:
            json.dump(sensor_data, f, indent=2)
        
        # Check if image was included
        if 'image' in data and data['image']:
            # Save image to file
            image_data = base64.b64decode(data['image'])
            with open(f'mock_server_data/images/fridge_{timestamp}.jpg', 'wb') as f:
                f.write(image_data)
            logger.info("Saved image to file")
        
        # Return success response
        return jsonify({
            'status': 'success',
            'message': 'Data received and processed successfully',
            'timestamp': timestamp
        })
        
    except Exception as e:
        logger.error(f"Error processing upload: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@app.route('/api/status', methods=['GET'])
def status():
    """Provide API status information"""
    # Count number of stored data points
    data_files = [f for f in os.listdir('mock_server_data') 
                 if f.startswith('sensor_data_') and f.endswith('.json')]
    
    # Count number of stored images
    image_files = [f for f in os.listdir('mock_server_data/images') 
                  if f.endswith('.jpg')]
    
    return jsonify({
        'status': 'online',
        'stored_data_points': len(data_files),
        'stored_images': len(image_files),
        'server_time': datetime.now().isoformat()
    })


if __name__ == '__main__':
    logger.info("========== Mock API Server Starting ==========")
    logger.info(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"API endpoint: http://localhost:5000/api/upload")
    
    # Run the Flask app
    app.run(host='0.0.0.0', port=5000, debug=True) 