from fastapi import APIRouter, HTTPException
import json
import os
import logging
from typing import Dict

# Import schemas
from schemas import FridgeStatusResponse

# Create router
router = APIRouter()

# Configure logging
logger = logging.getLogger(__name__)

# Path to store the fridge log data
FRIDGE_LOG_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "fridge_log.json")

@router.get("/fridge-status", response_model=FridgeStatusResponse, summary="Get current fridge status")
async def get_fridge_status():
    """
    Retrieve the current fridge status
    
    Returns the latest fridge status data from the log file
    """
    try:
        # Check if the log file exists
        if not os.path.exists(FRIDGE_LOG_PATH):
            logger.warning("Fridge log file not found")
            raise HTTPException(status_code=404, detail="No fridge data available. Please upload data first.")
        
        # Read the log file
        with open(FRIDGE_LOG_PATH, "r") as f:
            return json.load(f)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving fridge status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving fridge status: {str(e)}") 