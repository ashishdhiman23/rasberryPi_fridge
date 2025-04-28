from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime
import json
import os
import logging
from typing import Dict

# Import schemas and services
from schemas import SensorData, FridgeStatusResponse
from services.vision import vision_service
from agents.fridge_agent import fridge_agent

# Create router
router = APIRouter()

# Configure logging
logger = logging.getLogger(__name__)

# Path to store the fridge log data
FRIDGE_LOG_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "fridge_log.json")

# Helper function to load the current fridge log
async def load_fridge_log() -> Dict:
    """Load the current fridge log file"""
    try:
        if os.path.exists(FRIDGE_LOG_PATH):
            with open(FRIDGE_LOG_PATH, "r") as f:
                return json.load(f)
        else:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(FRIDGE_LOG_PATH), exist_ok=True)
            # Return empty default log
            return {
                "status": "ok",
                "timestamp": datetime.now().isoformat(),
                "temp": 0,
                "humidity": 0,
                "gas": 0,
                "items": [],
                "ai_response": None,
                "priority": ["safety", "freshness", "recipes"],
                "analysis": {
                    "safety": "No data available.",
                    "freshness": "No data available.",
                    "recipes": "No data available."
                }
            }
    except Exception as e:
        logger.error(f"Error loading fridge log: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error loading fridge log: {str(e)}")

# Helper function to save the fridge log
async def save_fridge_log(data: Dict) -> None:
    """Save data to the fridge log file"""
    try:
        with open(FRIDGE_LOG_PATH, "w") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        logger.error(f"Error saving fridge log: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error saving fridge log: {str(e)}")

@router.post("/upload", response_model=FridgeStatusResponse, summary="Upload fridge sensor data and image")
async def upload_fridge_data(sensor_data: SensorData):
    """
    Upload sensor data and image from the Raspberry Pi
    
    - Processes the image using GPT-4 Vision to detect food items
    - Analyzes the data using FridgeAgent
    - Saves the results to the fridge log
    
    Returns the processed fridge status
    """
    try:
        # Step 1: Detect food items with GPT-4 Vision
        logger.info("Processing image with Vision API")
        items = await vision_service.detect_food_items(sensor_data.image_base64)
        
        # Step 2: Analyze data with FridgeAgent
        logger.info("Analyzing data with FridgeAgent")
        analysis = await fridge_agent.analyze(
            temp=sensor_data.temp,
            humidity=sensor_data.humidity,
            gas=sensor_data.gas,
            items=items
        )
        
        # Step 3: Create the fridge status response
        fridge_status = {
            "status": "ok",
            "timestamp": datetime.now().isoformat(),
            "temp": sensor_data.temp,
            "humidity": sensor_data.humidity,
            "gas": sensor_data.gas,
            "items": items,
            "ai_response": analysis.get("ai_response"),
            "priority": analysis.get("priority", ["safety", "freshness", "recipes"]),
            "analysis": analysis.get("analysis", {
                "safety": "Analysis not available.",
                "freshness": "Analysis not available.",
                "recipes": "Analysis not available."
            })
        }
        
        # Step 4: Save the fridge status to the log file
        await save_fridge_log(fridge_status)
        
        return fridge_status
        
    except Exception as e:
        logger.error(f"Error processing fridge data: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing fridge data: {str(e)}") 