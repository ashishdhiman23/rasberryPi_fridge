from fastapi import FastAPI, APIRouter, File, UploadFile, Form, Body
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
import json
import base64
from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel
import httpx
from dotenv import load_dotenv
from utils.logger import log_request, log_response, log_error, log_api_call

# Load environment variables from .env file
load_dotenv()

# Define Pydantic models for request/response
class ChatRequest(BaseModel):
    user_message: str
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    status: str
    timestamp: str
    session_id: Optional[str] = None

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
    response = {
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
    log_response(response, "/")
    return response

# Simple API endpoint for testing
@app.get("/api/status")
async def status():
    response = {
        "status": "online",
        "message": "API is running",
        "timestamp": datetime.now().isoformat(),
        "server_info": {
            "render_instance": os.getenv("RENDER_INSTANCE_ID", "unknown"),
            "python_version": os.getenv("PYTHON_VERSION", "3.x")
        }
    }
    log_response(response, "/api/status")
    return response

# Endpoint for the frontend to get fridge status
@app.get("/api/fridge-status")
async def fridge_status():
    response = {
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
    log_response(response, "/api/fridge-status")
    return response

# Chat endpoint for conversing with the fridge
@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        log_request(request.dict(), "/api/chat")
        
        # Get the last fridge status to provide context to the model
        fridge_data = {
            "temp": 4.2,
            "humidity": 52.3,
            "gas": 125,
            "items": ["milk", "eggs", "cheese", "yogurt", "leftovers"],
        }
        
        # Get OpenAI API key from environment
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            error_msg = "WARNING: OPENAI_API_KEY not found in environment variables"
            print(error_msg)
            response = {
                "response": "I'm sorry, but I'm not able to process your request right now due to configuration issues.",
                "status": "error",
                "timestamp": datetime.now().isoformat(),
                "session_id": request.session_id
            }
            log_response(response, "/api/chat")
            return response
            
        # Create a system prompt with the fridge information
        system_prompt = f"""
        You are a helpful assistant for a Smart Fridge. You can answer questions about the contents
        of the fridge and provide recommendations based on the current inventory.
        
        Current fridge status:
        - Temperature: {fridge_data['temp']}°C
        - Humidity: {fridge_data['humidity']}%
        - Gas Level: {fridge_data['gas']} PPM
        - Food items: {', '.join(fridge_data['items'])}
        
        Be helpful, concise, and natural in your responses. If the user asks about food items not in the
        fridge, you can politely inform them that those items aren't currently detected.
        """
        
        # Prepare OpenAI API request
        openai_request = {
            "model": "gpt-4",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": request.user_message}
            ],
            "max_tokens": 500
        }
        
        # Call OpenAI API for chat completion
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                },
                json=openai_request
            )
            
            # Log the API call
            log_api_call("OpenAI Chat Completion", openai_request, response.json())
            
            # Check for errors
            response.raise_for_status()
            result = response.json()
            
            # Extract assistant's response
            assistant_response = result["choices"][0]["message"]["content"]
            
            # Prepare and log the response
            chat_response = {
                "response": assistant_response,
                "status": "ok",
                "timestamp": datetime.now().isoformat(),
                "session_id": request.session_id
            }
            log_response(chat_response, "/api/chat")
            return chat_response
            
    except Exception as e:
        log_error(e, "/api/chat")
        response = {
            "response": "I'm sorry, but I'm having trouble understanding right now. Please try again later.",
            "status": "error",
            "timestamp": datetime.now().isoformat(),
            "session_id": request.session_id
        }
        log_response(response, "/api/chat")
        return response

# Simple upload endpoint that matches the simulator's expected endpoint
@app.post("/api/upload/multipart")
async def upload_multipart(
    data: str = Form(...),
    image: Optional[UploadFile] = File(None)
):
    try:
        # Log the incoming request
        request_data = {
            "data": data,
            "image_filename": image.filename if image else None
        }
        log_request(request_data, "/api/upload/multipart")
        
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
        
        response = {
            "status": "success",
            "message": "Data received and processed",
            "timestamp": datetime.now().isoformat(),
            "image_processed": image_processed,
            "food_items": ["milk", "eggs"],
            "temperature_status": "normal" if 2 <= sensor_data.get("temp", 4) <= 5 else "warning"
        }
        log_response(response, "/api/upload/multipart")
        return response
    except Exception as e:
        log_error(e, "/api/upload/multipart")
        response = {
            "status": "error",
            "message": f"Error processing upload: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }
        log_response(response, "/api/upload/multipart")
        return response

# Run the app with uvicorn if executed directly
if __name__ == "__main__":
    # Get port from environment variable for cloud platforms
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True) 