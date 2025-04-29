from fastapi import FastAPI, APIRouter, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
import json
import base64
from typing import Optional
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Create FastAPI app
app = FastAPI(
    title="Smart Fridge AI API",
    description="Backend API for Smart Fridge system with GPT-4 Vision and "
                "multiple OpenAI Assistants",
    version="1.0.0"
)

# Get allowed origins from environment variable or use default
allowed_origins = os.getenv("ALLOWED_ORIGINS", "*").split(",")
print(f"Allowed origins: {allowed_origins}")

# Setup CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create placeholder routers - we'll implement a basic API without the complex imports
upload_router = APIRouter()
status_router = APIRouter()
notifications_router = APIRouter()
chat_router = APIRouter()

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Welcome to Smart Fridge AI API", 
        "status": "online",
        "features": [
            "GPT-4 Vision food detection",
            "Multi-agent system with specialized agents",
            "Safety, freshness, and recipe analysis",
            "Expiration date tracking",
            "Real-time notifications"
        ]
    }

# Simple API endpoint for testing
@app.get("/api/status")
async def status():
    return {
        "status": "online",
        "message": "API is running",
        "timestamp": datetime.now().isoformat(),
        "server_info": {
            "render_instance": os.getenv("RENDER_INSTANCE_ID", "unknown"),
            "python_version": os.getenv("PYTHON_VERSION", "3.x")
        }
    }

# Endpoint for the frontend to get fridge status
@app.get("/api/fridge-status")
async def fridge_status():
    # Return mock fridge status data for now
    return {
        "temp": 4.2,
        "humidity": 52.3,
        "gas": 125,
        "items": ["milk", "eggs", "cheese", "yogurt", "leftovers"],
        "priority": ["milk (expires soon)", "leftovers (3d old)"],
        "analysis": {
            "freshness": "All items appear fresh",
            "safety": "Temperature is in the safe range (2-5°C)",
            "fill_level": "Fridge is 60% full",
            "recommendations": "Consider consuming milk soon"
        },
        "timestamp": datetime.now().isoformat()
    }

# Simple upload endpoint that matches the simulator's expected endpoint
@app.post("/api/upload/multipart")
async def upload_multipart(
    data: str = Form(...),
    image: Optional[UploadFile] = File(None)
):
    try:
        # Parse the JSON data
        sensor_data = json.loads(data)
        
        # Process image if provided
        image_processed = False
        if image:
            # In a real implementation, we would process the image
            # For now, we'll just acknowledge receipt
            image_processed = True
        
        # Log the received data
        print(f"Received sensor data: {sensor_data}")
        if image:
            print(f"Received image: {image.filename}")
        
        return {
            "status": "success",
            "message": "Data received and processed",
            "timestamp": datetime.now().isoformat(),
            "image_processed": image_processed,
            "food_items": ["milk", "eggs"],
            "temperature_status": "normal" if 2 <= sensor_data.get("temp", 4) <= 5 else "warning"
        }
    except Exception as e:
        print(f"Error processing upload: {str(e)}")
        return {
            "status": "error",
            "message": f"Error processing upload: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }

# Run the app with uvicorn if executed directly
if __name__ == "__main__":
    # Get port from environment variable for cloud platforms
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True) 