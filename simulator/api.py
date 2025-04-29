"""
API routes for the Smart Fridge Simulator.
Provides endpoints for interacting with the fridge, including the chat feature.
"""
import json
import uuid
import os
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from simulator.chat_agent import ChatAgent

# Initialize FastAPI app
app = FastAPI(
    title="Smart Fridge API",
    description="API for interacting with the Smart Fridge Simulator",
    version="1.0.0"
)

# Add CORS middleware to allow requests from the dashboard
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize chat agent
chat_agent = ChatAgent()

# Path to data files
SIMULATOR_DIR = Path("simulator")
LAST_UPLOAD_FILE = SIMULATOR_DIR / "last_upload.json"
LAST_API_RESPONSE_FILE = SIMULATOR_DIR / "last_api_response.json"
MOCK_IMAGES_DIR = SIMULATOR_DIR / "mock_images"
DASHBOARD_DIR = Path("dashboard")

# Serve dashboard static files
app.mount("/dashboard", StaticFiles(directory=str(DASHBOARD_DIR), html=True), name="dashboard")
app.mount("/simulator/mock_images", StaticFiles(directory=str(MOCK_IMAGES_DIR)), name="images")

# Pydantic models for request/response validation
class ChatRequest(BaseModel):
    """Request model for the chat endpoint."""
    user_message: str = Field(..., description="Question or command from the user")
    session_id: Optional[str] = Field(None, description="Session ID for conversation tracking")
    include_image: bool = Field(False, description="Whether to include the latest fridge image")
    timestamp: Optional[str] = Field(None, description="Timestamp for the fridge snapshot")

class ChatResponse(BaseModel):
    """Response model for the chat endpoint."""
    response: str = Field(..., description="Response from the AI assistant")
    status: str = Field("ok", description="Status of the request (ok or error)")
    error: Optional[str] = Field(None, description="Error message if status is error")
    timestamp: str = Field(..., description="Timestamp of the response")

@app.post("/api/chat", response_model=ChatResponse, tags=["Chat"])
async def chat_with_fridge(request: ChatRequest) -> Dict[str, Any]:
    """
    Chat with the smart fridge AI assistant.
    
    Allows users to ask questions about their fridge contents and get AI-powered responses.
    Optionally includes the latest fridge image for visual context.
    """
    # Generate a session ID if not provided
    session_id = request.session_id or str(uuid.uuid4())
    
    # Get response from chat agent
    result = await chat_agent.get_chat_response(
        user_message=request.user_message,
        session_id=session_id,
        include_image=request.include_image
    )
    
    # Add timestamp to the response
    result["timestamp"] = datetime.now().isoformat()
    
    # Return the response
    if result["status"] != "ok":
        # Still return a 200 status code to the client but with error info
        return result
    return result

@app.get("/api/status", tags=["Status"])
async def get_status() -> Dict[str, Any]:
    """Get the status of the API."""
    return {
        "status": "online",
        "timestamp": datetime.now().isoformat(),
        "features": ["chat_with_fridge", "sensor_data", "image_capture"]
    }

@app.get("/api/last_data", tags=["Data"])
async def get_last_data() -> Dict[str, Any]:
    """
    Get the last uploaded sensor data and food items.
    
    This endpoint combines sensor data from last_upload.json and
    food items from last_api_response.json for the dashboard to display.
    """
    try:
        # Read sensor data
        sensor_data = {}
        if LAST_UPLOAD_FILE.exists():
            with open(LAST_UPLOAD_FILE, "r") as f:
                sensor_data = json.load(f)
        
        # Read API response for food items
        food_items = {}
        if LAST_API_RESPONSE_FILE.exists():
            try:
                with open(LAST_API_RESPONSE_FILE, "r") as f:
                    api_data = json.load(f)
                
                # Extract food items if they exist
                if "food_items" in api_data:
                    for item in api_data["food_items"]:
                        if "name" in item and "detected_at" in item:
                            days_ago = (datetime.now() - datetime.fromisoformat(item["detected_at"])).days
                            food_items[item["name"]] = days_ago
            except json.JSONDecodeError:
                pass  # Ignore invalid JSON
        
        # Get the latest image timestamp
        latest_image_path = None
        latest_image_time = 0
        if MOCK_IMAGES_DIR.exists():
            for img_path in MOCK_IMAGES_DIR.glob("fridge_*.jpg"):
                if img_path.is_file():
                    img_time = img_path.stat().st_mtime
                    if img_time > latest_image_time:
                        latest_image_time = img_time
                        latest_image_path = img_path
        
        image_info = None
        if latest_image_path:
            image_time = datetime.fromtimestamp(latest_image_time)
            relative_path = latest_image_path.relative_to(os.getcwd())
            image_info = {
                "path": f"/simulator/mock_images/{latest_image_path.name}",
                "timestamp": image_time.isoformat()
            }
        
        # Combine data
        result = {
            "temp": sensor_data.get("temp"),
            "humidity": sensor_data.get("humidity"),
            "gas": sensor_data.get("gas"),
            "timestamp": sensor_data.get("timestamp", datetime.now().isoformat()),
            "last_seen": food_items,
            "image": image_info
        }
        
        return result
    
    except Exception as e:
        # Log the error but return a default response
        print(f"Error getting last data: {str(e)}")
        return {
            "temp": None,
            "humidity": None,
            "gas": None,
            "timestamp": datetime.now().isoformat(),
            "last_seen": {},
            "image": None
        }

# Root redirect to dashboard
@app.get("/", tags=["Dashboard"])
async def redirect_to_dashboard():
    """Redirect to the dashboard interface."""
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/dashboard/index.html") 