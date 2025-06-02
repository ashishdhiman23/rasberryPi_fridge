from fastapi import FastAPI, File, UploadFile, Form, HTTPException
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
from backend.utils.logger import log_request, log_response, log_error, log_api_call
from backend.image_guardrail import should_process_with_gpt_vision
from backend.utils import db

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

from backend.routes import items as items_router
app.include_router(items_router.router)

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
            "model": "gpt-4o",
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
                
                # Try to parse JSON response (handle markdown code blocks)
                try:
                    # First try direct JSON parsing
                    analysis_result = json.loads(vision_response)
                    return analysis_result
                except json.JSONDecodeError:
                    # Try to extract JSON from markdown code blocks
                    try:
                        # Look for JSON within ```json ... ``` blocks
                        import re
                        json_match = re.search(r'```json\s*\n(.*?)\n```', vision_response, re.DOTALL)
                        if json_match:
                            json_content = json_match.group(1)
                            analysis_result = json.loads(json_content)
                            return analysis_result
                    except (json.JSONDecodeError, AttributeError):
                        pass
                    
                    # If still no JSON, extract food items from text
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
        "water", "soda", "beer", "wine", "condiments", "sauce", "jam",
        "mangoes", "mango", "pineapple", "bananas", "banana", "grapes", "berries"
    ]
    
    found_items = []
    text_lower = text.lower()
    
    for food in common_foods:
        if food in text_lower:
            found_items.append(food)
    
    return found_items if found_items else ["milk", "eggs"]  # fallback


def generate_recipe_suggestions(food_items: list) -> str:
    """Generate recipe suggestions based on detected food items"""
    if not food_items:
        return "No specific recipes available. Please add some food items to your fridge!"
    
    # Recipe suggestions based on common food combinations
    recipes = []
    
    # Fruit-based recipes
    fruits = ["mangoes", "mango", "pineapple", "apples", "bananas", "banana", "grapes", "berries", "oranges"]
    detected_fruits = [item for item in food_items if item.lower() in fruits]
    
    if detected_fruits:
        if len(detected_fruits) >= 2:
            recipes.append(f"🥗 Fresh Fruit Salad with {', '.join(detected_fruits[:3])}")
        recipes.append(f"🥤 Smoothie with {detected_fruits[0]}")
        if "mangoes" in detected_fruits or "mango" in detected_fruits:
            recipes.append("🥭 Mango Lassi or Mango Sticky Rice")
        if "pineapple" in detected_fruits:
            recipes.append("🍍 Grilled Pineapple or Pineapple Upside-down Cake")
    
    # Vegetable-based recipes
    vegetables = ["carrots", "lettuce", "tomatoes", "onions", "potatoes"]
    detected_vegetables = [item for item in food_items if item.lower() in vegetables]
    
    if detected_vegetables:
        recipes.append(f"🥗 Fresh Salad with {', '.join(detected_vegetables[:2])}")
        if "potatoes" in detected_vegetables:
            recipes.append("🥔 Roasted Potatoes or Mashed Potatoes")
    
    # Dairy and protein combinations
    if "eggs" in food_items and "milk" in food_items:
        recipes.append("🍳 Scrambled Eggs or French Toast")
    elif "eggs" in food_items:
        recipes.append("🥚 Boiled Eggs or Omelet")
    
    if not recipes:
        return f"Try using your {', '.join(food_items[:3])} in a healthy meal or snack!"
    
    return " • ".join(recipes[:4])  # Limit to 4 suggestions

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
    image: Optional[UploadFile] = File(None),
    username: str = Form(None)
):
    global latest_fridge_data
    
    try:
        if not username:
            raise HTTPException(status_code=400, detail="Username is required")

        # Log the incoming request
        request_data = {
            "data": data,
            "image_filename": image.filename if image else None,
            "image_size": len(await image.read()) if image else 0,
            "username": username
        }
        log_request(request_data, "/api/upload/multipart")
        
        # Reset file pointer after reading for size
        if image:
            await image.seek(0)
        
        # Parse the JSON data
        sensor_data = json.loads(data)
        
        # Process image with GPT-4 Vision if provided
        vision_analysis = None
        guardrail_result = None
        user_id = await db.add_user(username)
        
        if image:
            print(f"Processing image: {image.filename} ({request_data['image_size']} bytes)")
            image_data = await image.read()
            
            # Apply guardrail to check if image contains food
            should_process, guardrail_analysis = should_process_with_gpt_vision(image_data)
            guardrail_result = guardrail_analysis
            
            print(f"Guardrail analysis: {guardrail_analysis}")
            
            if should_process:
                print("✅ Guardrail passed - processing with GPT-4 Vision")
                vision_analysis = await analyze_fridge_image(image_data)
                # Update user's item list with detected items
                for item_name in vision_analysis.get("food_items", []):
                    await db.add_or_update_item(user_id, item_name, 1)
            else:
                print("❌ Guardrail blocked - image doesn't appear to contain food")
                # Create a mock analysis for non-food images
                vision_analysis = {
                    "food_items": [],
                    "analysis": f"Image analysis skipped - {guardrail_analysis.get('method', 'guardrail')} detected this may not be a food image (confidence: {guardrail_analysis.get('food_confidence', 0):.2f})",
                    "confidence": "low",
                    "safety_notes": "No food items detected in image"
                }
            
            # Structure analysis for frontend
            analysis_text = vision_analysis.get("analysis", "")
            # Use the user's item list for AI analysis
            user_items = await db.get_items(user_id)
            food_items = [item["name"] for item in user_items]
            
            # Generate recipe suggestions based on detected items
            recipe_suggestions = generate_recipe_suggestions(food_items)
            
            structured_analysis = {
                "safety": vision_analysis.get("safety_notes", "No safety concerns detected."),
                "freshness": analysis_text,
                "recipes": recipe_suggestions
            }
            
            # Update global fridge data with vision analysis
            latest_fridge_data.update({
                "temp": sensor_data.get("temp", 4.2),
                "humidity": sensor_data.get("humidity", 52.3),
                "gas": sensor_data.get("gas", 125),
                "items": food_items,
                "last_updated": datetime.now().isoformat(),
                "vision_analysis": analysis_text,
                "analysis": structured_analysis,
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
            "food_items": latest_fridge_data["items"],
            "temperature_status": "normal" if 2 <= sensor_data.get("temp", 4) <= 5 else "warning",
            "vision_confidence": vision_analysis.get("confidence", "none") if vision_analysis else "none",
            "analysis": vision_analysis.get("analysis", "") if vision_analysis else "",
            "guardrail": guardrail_result if guardrail_result else None
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