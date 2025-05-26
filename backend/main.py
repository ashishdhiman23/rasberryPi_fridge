from fastapi import FastAPI, File, UploadFile, Form
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

# Store the latest fridge data globally for chat context
latest_fridge_data = {
    "temp": 4.2,
    "humidity": 52.3,
    "gas": 125,
    "items": ["milk", "eggs", "cheese", "yogurt", "leftovers"],
    "last_updated": datetime.now().isoformat()
}

async def analyze_fridge_image(image_data: bytes) -> Dict[str, Any]:
    """
    Analyze fridge image using GPT-4 Vision to detect food items
    
    Args:
        image_data: Raw image bytes
        
    Returns:
        Dict containing detected food items and analysis
    """
    try:
        # Get OpenAI API key
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            print("WARNING: OPENAI_API_KEY not found")
            return {
                "food_items": ["milk", "eggs"],  # fallback
                "analysis": "Unable to analyze image - API key not configured",
                "confidence": "low"
            }
        
        # Convert image to base64
        image_base64 = base64.b64encode(image_data).decode('utf-8')
        
        # Prepare GPT-4 Vision request
        vision_request = {
            "model": "gpt-4-vision-preview",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": """Analyze this refrigerator image and identify all visible food items. 
                            Please provide:
                            1. A list of specific food items you can clearly see
                            2. Brief analysis of freshness/condition if visible
                            3. Any safety concerns
                            
                            Format your response as JSON with these fields:
                            - food_items: array of specific food item names
                            - analysis: brief text analysis
                            - safety_notes: any safety concerns
                            - confidence: high/medium/low based on image clarity"""
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_base64}"
                            }
                        }
                    ]
                }
            ],
            "max_tokens": 500
        }
        
        # Call OpenAI Vision API
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                },
                json=vision_request
            )
            
            log_api_call("OpenAI Vision Analysis", vision_request, response.json())
            
            if response.status_code == 200:
                result = response.json()
                vision_response = result["choices"][0]["message"]["content"]
                
                # Try to parse JSON response
                try:
                    analysis_result = json.loads(vision_response)
                    return analysis_result
                except json.JSONDecodeError:
                    # If not JSON, extract food items from text
                    return {
                        "food_items": extract_food_items_from_text(vision_response),
                        "analysis": vision_response,
                        "confidence": "medium"
                    }
            else:
                print(f"Vision API error: {response.status_code} - {response.text}")
                return {
                    "food_items": ["milk", "eggs"],  # fallback
                    "analysis": f"Vision API error: {response.status_code}",
                    "confidence": "low"
                }
                
    except Exception as e:
        print(f"Error in image analysis: {e}")
        return {
            "food_items": ["milk", "eggs"],  # fallback
            "analysis": f"Error analyzing image: {str(e)}",
            "confidence": "low"
        }

def extract_food_items_from_text(text: str) -> list:
    """Extract food items from text response if JSON parsing fails"""
    # Simple extraction - look for common food words
    common_foods = [
        "milk", "eggs", "cheese", "yogurt", "butter", "bread", "meat", "chicken",
        "beef", "fish", "vegetables", "fruits", "apples", "oranges", "carrots",
        "lettuce", "tomatoes", "onions", "potatoes", "leftovers", "juice",
        "water", "soda", "beer", "wine", "condiments", "sauce", "jam"
    ]
    
    found_items = []
    text_lower = text.lower()
    
    for food in common_foods:
        if food in text_lower:
            found_items.append(food)
    
    return found_items if found_items else ["milk", "eggs"]  # fallback

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
    global latest_fridge_data
    log_response(latest_fridge_data, "/api/fridge-status")
    return latest_fridge_data

# Chat endpoint for conversing with the fridge
@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        log_request(request.dict(), "/api/chat")
        
        # Use the latest fridge data from image analysis
        global latest_fridge_data
        
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
            
        # Create a system prompt with the latest fridge information
        system_prompt = f"""
        You are a helpful assistant for a Smart Fridge. You can answer questions about the contents
        of the fridge and provide recommendations based on the current inventory.
        
        Current fridge status (last updated: {latest_fridge_data.get('last_updated', 'unknown')}):
        - Temperature: {latest_fridge_data['temp']}°C
        - Humidity: {latest_fridge_data['humidity']}%
        - Gas Level: {latest_fridge_data['gas']} PPM
        - Food items: {', '.join(latest_fridge_data['items'])}
        
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

# Improved upload endpoint with actual image processing
@app.post("/api/upload/multipart")
async def upload_multipart(
    data: str = Form(...),
    image: Optional[UploadFile] = File(None)
):
    global latest_fridge_data
    
    try:
        # Log the incoming request
        request_data = {
            "data": data,
            "image_filename": image.filename if image else None,
            "image_size": len(await image.read()) if image else 0
        }
        log_request(request_data, "/api/upload/multipart")
        
        # Reset file pointer after reading for size
        if image:
            await image.seek(0)
        
        # Parse the JSON data
        sensor_data = json.loads(data)
        
        # Process image with GPT-4 Vision if provided
        vision_analysis = None
        if image:
            print(f"Processing image: {image.filename} ({request_data['image_size']} bytes)")
            image_data = await image.read()
            vision_analysis = await analyze_fridge_image(image_data)
            
            # Update global fridge data with vision analysis
            latest_fridge_data.update({
                "temp": sensor_data.get("temp", 4.2),
                "humidity": sensor_data.get("humidity", 52.3),
                "gas": sensor_data.get("gas", 125),
                "items": vision_analysis.get("food_items", ["milk", "eggs"]),
                "last_updated": datetime.now().isoformat(),
                "vision_analysis": vision_analysis.get("analysis", ""),
                "confidence": vision_analysis.get("confidence", "medium")
            })
        else:
            # Update sensor data only
            latest_fridge_data.update({
                "temp": sensor_data.get("temp", 4.2),
                "humidity": sensor_data.get("humidity", 52.3),
                "gas": sensor_data.get("gas", 125),
                "last_updated": datetime.now().isoformat()
            })
        
        # Log the received data
        print(f"Received sensor data: {sensor_data}")
        if vision_analysis:
            print(f"Vision analysis: {vision_analysis}")
        
        response = {
            "status": "success",
            "message": "Data received and processed with AI vision",
            "timestamp": datetime.now().isoformat(),
            "image_processed": image is not None,
            "food_items": vision_analysis.get("food_items", ["milk", "eggs"]) if vision_analysis else latest_fridge_data["items"],
            "temperature_status": "normal" if 2 <= sensor_data.get("temp", 4) <= 5 else "warning",
            "vision_confidence": vision_analysis.get("confidence", "none") if vision_analysis else "none",
            "analysis": vision_analysis.get("analysis", "") if vision_analysis else ""
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