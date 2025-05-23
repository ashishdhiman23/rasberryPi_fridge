# Smart Fridge Raspberry Pi System

This project implements a smart fridge monitoring system using Raspberry Pi (or a simulator for testing). The system captures temperature, humidity, and gas levels, takes images of the fridge interior, and provides an AI-powered chat interface.

## Components

- **Raspberry Pi Module**: Captures real sensor data and images
- **Simulator**: Emulates sensor data and camera for testing without hardware
- **Backend API**: Provides endpoints for data upload and AI-powered chat
- **Dashboard**: Web interface for monitoring and interacting with the fridge

## Setting Up

### Requirements

- Python 3.8 or higher
- Required Python packages (install with `pip install -r requirements.txt`)
- OpenAI API key for chat functionality

### Installation

1. Clone this repository
2. Create a `.env` file in the `backend` directory with your OpenAI API key:
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   ```
3. Install dependencies:
   ```
   pip install -r requirements.txt
   pip install -r backend/requirements.txt
   pip install -r simulator/requirements.txt
   ```

## Running the System

### Starting the Backend Server

```
python run_backend.py
```

This will start the backend server on http://localhost:8000.

### Starting the Simulator

```
python run_simulator.py
```

Optional arguments:
- `--interval`: Monitoring interval in seconds (default: 30)
- `--image-interval`: Image capture interval in seconds (default: 60)
- `--real-api`: Use real API endpoint instead of simulating

## Using the Dashboard

1. Open http://localhost:8000/dashboard in your web browser
2. The dashboard displays:
   - Current sensor readings (temperature, humidity, gas levels)
   - Latest fridge image
   - Detected food items
   - Chat interface to interact with your fridge

## Chat Feature

The Smart Fridge includes an AI-powered chat feature that allows you to interact with your fridge. You can:

- Ask about food items in your fridge
- Get recipe suggestions based on available ingredients
- Ask about fridge temperature and conditions
- Get food safety and freshness advice

To use the chat:
1. Enter your question in the chat input at the bottom of the dashboard
2. Toggle "Include fridge image" if you want the AI to analyze the current fridge image
3. Click "Send" or press Enter to get a response

Example questions:
- "What's in my fridge?"
- "Is my fridge temperature safe?"
- "What can I make with the ingredients I have?"
- "How long will my milk last?"

## Troubleshooting

- **Chat feature not working**: Ensure you have a valid OpenAI API key in the backend/.env file
- **Simulator fails to start**: Check that all required packages are installed
- **Dashboard not loading**: Make sure the backend server is running
