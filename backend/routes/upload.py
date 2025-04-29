from fastapi import APIRouter, HTTPException, Depends, File, UploadFile, Form
from fastapi.responses import JSONResponse
from datetime import datetime
import json
import os
import logging
import base64
from typing import Dict, Optional

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

# Support for backwards compatibility with base64 JSON uploads
@router.post("/upload", response_model=FridgeStatusResponse, summary="Upload fridge sensor data and image")
async def upload_fridge_data(sensor_data: SensorData):
    """
    Upload sensor data and image from the Raspberry Pi using JSON with base64 encoding
    
    This endpoint is maintained for backwards compatibility.
    """
    logger.info("Received base64 JSON upload (legacy method)")
    try:
        # Check if debug mode is enabled (not part of schema, but can be in request body)
        debug_mode = False
        if hasattr(sensor_data, "__dict__") and "debug" in sensor_data.__dict__:
            debug_mode = sensor_data.__dict__["debug"]
            
        # Step 1: Detect food items with GPT-4 Vision
        logger.info("Processing image with Vision API")
        items = await vision_service.detect_food_items(sensor_data.image_base64)
        
        if debug_mode:
            logger.info(f"Vision API detected items: {items}")
            
        # Step 2: Analyze data with FridgeAgent
        logger.info("Analyzing data with FridgeAgent")
        analysis = await fridge_agent.analyze(
            temp=sensor_data.temp,
            humidity=sensor_data.humidity,
            gas=sensor_data.gas,
            items=items
        )
        
        # Step 3: Create the fridge status response
        fridge_status = await create_fridge_status(
            temp=sensor_data.temp,
            humidity=sensor_data.humidity,
            gas=sensor_data.gas,
            items=items,
            analysis=analysis
        )
        
        return fridge_status
        
    except Exception as e:
        logger.error(f"Error processing fridge data: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing fridge data: {str(e)}")

# New endpoint for multipart/form-data uploads
@router.post("/upload/multipart", response_model=FridgeStatusResponse, summary="Upload fridge data with multipart/form-data")
async def upload_multipart(
    image: UploadFile = File(...),
    temp: float = Form(...),
    humidity: float = Form(...),
    gas: int = Form(...),
    debug: Optional[bool] = Form(False)
):
    """
    Upload sensor data and image using multipart/form-data for more efficient transfer
    
    - Accepts image file directly instead of base64 encoding
    - More bandwidth-efficient than the base64 JSON method
    - Processes the image using GPT-4 Vision to detect food items
    - Analyzes the data using FridgeAgent
    - Saves the results to the fridge log
    """
    logger.info("Received multipart/form-data upload (efficient method)")
    try:
        # Read the image file
        image_content = await image.read()
        
        # Convert to base64 for Vision API
        image_base64 = base64.b64encode(image_content).decode('utf-8')
        
        # Step 1: Detect food items with GPT-4 Vision
        logger.info("Processing image with Vision API")
        items = await vision_service.detect_food_items(image_base64)
        
        if debug:
            logger.info(f"Vision API detected items: {items}")
            
        # Step 2: Analyze data with FridgeAgent
        logger.info("Analyzing data with FridgeAgent")
        analysis = await fridge_agent.analyze(
            temp=temp,
            humidity=humidity,
            gas=gas,
            items=items
        )
        
        # Step 3: Create the fridge status response
        fridge_status = await create_fridge_status(
            temp=temp,
            humidity=humidity,
            gas=gas,
            items=items,
            analysis=analysis
        )
        
        return fridge_status
        
    except Exception as e:
        logger.error(f"Error processing multipart fridge data: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing fridge data: {str(e)}")

# Helper function to create fridge status and notifications
async def create_fridge_status(temp, humidity, gas, items, analysis):
    """Create fridge status and generate notifications"""
    # Create the fridge status response
    fridge_status = {
        "status": "ok",
        "timestamp": datetime.now().isoformat(),
        "temp": temp,
        "humidity": humidity,
        "gas": gas,
        "items": items,
        "ai_response": analysis.get("ai_response"),
        "priority": analysis.get("priority", ["safety", "expiration", "freshness", "recipes"]),
        "analysis": analysis.get("analysis", {
            "safety": "Analysis not available.",
            "freshness": "Analysis not available.",
            "recipes": "Analysis not available.",
            "expiration": "Analysis not available."
        })
    }
    
    # Save the fridge status to the log file
    await save_fridge_log(fridge_status)
    
    # Generate notifications based on analysis
    try:
        from routes.notifications import create_notification
        
        # Safety notifications (high priority)
        safety_analysis = fridge_status["analysis"].get("safety", "")
        if "🚨" in safety_analysis:
            # Danger notification (priority 1)
            create_notification(
                type="alert",
                title="Safety Alert: Fridge Condition Critical",
                message=safety_analysis,
                priority=1
            )
        elif "🟡" in safety_analysis:
            # Warning notification (priority 2)
            create_notification(
                type="alert",
                title="Safety Warning: Fridge Needs Attention",
                message=safety_analysis,
                priority=2
            )
        
        # Expiration notifications (medium priority)
        expiration_analysis = fridge_status["analysis"].get("expiration", "")
        if "🚨" in expiration_analysis:
            # Expired items notification
            create_notification(
                type="expiry",
                title="Food Expired: Immediate Attention Required",
                message=expiration_analysis,
                priority=1
            )
        elif "🟡" in expiration_analysis and "Expiring Soon" in expiration_analysis:
            # Expiring soon notification
            create_notification(
                type="expiry",
                title="Items Expiring Soon",
                message=expiration_analysis,
                priority=2
            )
        
        # Freshness notifications (lower priority)
        freshness_analysis = fridge_status["analysis"].get("freshness", "")
        if any(term in freshness_analysis.lower() for term in ["consume", "soon", "use", "old"]):
            create_notification(
                type="info",
                title="Freshness Update",
                message=freshness_analysis,
                priority=3
            )
        
        logger.info("Generated notifications from analysis")
    except Exception as e:
        logger.error(f"Error generating notifications: {str(e)}")
    
    return fridge_status 