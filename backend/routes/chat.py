from fastapi import APIRouter, HTTPException, Depends, Body
from fastapi.security import APIKeyHeader
from typing import Dict, Any, Optional
import os
import json
import logging
import uuid
from datetime import datetime
import httpx

from backend.schemas import ChatRequest, ChatResponse

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize router
router = APIRouter(
    prefix="/chat",
    tags=["chat"],
    responses={404: {"description": "Not found"}},
)

# Constants
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
os.makedirs(DATA_DIR, exist_ok=True)

# Path to store chat history
CHAT_HISTORY_FILE = os.path.join(DATA_DIR, "chat_history.json")

# Default system prompt
DEFAULT_SYSTEM_PROMPT = """
You are a smart fridge assistant. You help the user make decisions based on the 
current temperature, humidity, gas levels, and visible food items in their fridge.
Be helpful, concise, and practical. If the temperature is outside of safe range (1-5°C),
warn the user. For food items, consider freshness based on when they were last seen.
"""

# OpenAI API key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    logger.warning("OPENAI_API_KEY not found in environment variables")

# Function to get the latest fridge data
async def get_latest_fridge_data() -> Dict[str, Any]:
    """
    Get the latest fridge data including sensor readings and food items.
    
    Returns:
        Dictionary containing current fridge data
    """
    try:
        # Path to last status file
        status_file = os.path.join(DATA_DIR, "last_status.json")
        
        # If file exists, read it
        if os.path.exists(status_file):
            with open(status_file, "r") as f:
                data = json.load(f)
                return data
        
        # Fallback to default values if file doesn't exist
        return {
            "temp": None,
            "humidity": None,
            "gas": None,
            "items": [],
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting latest fridge data: {e}")
        # Return empty/default data in case of error
        return {
            "temp": None,
            "humidity": None,
            "gas": None,
            "items": [],
            "timestamp": datetime.now().isoformat()
        }

# Function to save chat history
async def save_chat_history(session_id: str, user_message: str, assistant_response: str) -> None:
    """
    Save chat history to a JSON file.
    
    Args:
        session_id: Unique session identifier
        user_message: User's message
        assistant_response: Assistant's response
    """
    try:
        # Create history structure
        history = {"sessions": {}}
        
        # Load existing history if available
        if os.path.exists(CHAT_HISTORY_FILE):
            with open(CHAT_HISTORY_FILE, "r") as f:
                history = json.load(f)
        
        # Create session if it doesn't exist
        if session_id not in history["sessions"]:
            history["sessions"][session_id] = []
        
        # Add message pair to history
        history["sessions"][session_id].append({
            "timestamp": datetime.now().isoformat(),
            "user": user_message,
            "assistant": assistant_response
        })
        
        # Save updated history
        with open(CHAT_HISTORY_FILE, "w") as f:
            json.dump(history, f, indent=2)
            
    except Exception as e:
        logger.error(f"Error saving chat history: {str(e)}")

# Function to format GPT prompt with fridge data
def format_prompt(user_message: str, fridge_data: Dict[str, Any]) -> Dict:
    """
    Format the prompt for the GPT-4 API with fridge data.
    
    Args:
        user_message: The user's message
        fridge_data: Current fridge data
        
    Returns:
        Formatted messages for the API
    """
    # Format the fridge status text
    food_items_text = ""
    if fridge_data.get("items") and len(fridge_data["items"]) > 0:
        food_items = []
        for item in fridge_data["items"]:
            food_items.append(item)
        food_items_text = "- Food items seen: " + ", ".join(food_items)
    else:
        food_items_text = "- No food items detected"
    
    fridge_status = f"""
Here is my latest fridge status:
- Temperature: {fridge_data['temp'] if fridge_data.get('temp') is not None else 'Unknown'} °C
- Humidity: {fridge_data['humidity'] if fridge_data.get('humidity') is not None else 'Unknown'}%
- Gas Level: {fridge_data['gas'] if fridge_data.get('gas') is not None else 'Unknown'} PPM
{food_items_text}

User: "{user_message}"
"""
    
    # Create messages array
    messages = [
        {"role": "system", "content": DEFAULT_SYSTEM_PROMPT},
        {"role": "user", "content": fridge_status}
    ]
    
    return messages

@router.post("", response_model=ChatResponse)
async def chat_with_fridge(request: ChatRequest) -> Dict[str, Any]:
    """
    Chat with the smart fridge AI assistant.
    
    Allows users to ask questions about their fridge contents and get AI-powered responses.
    """
    if not OPENAI_API_KEY:
        return {
            "response": "OpenAI API key not configured. Please set the OPENAI_API_KEY environment variable.",
            "status": "error",
            "timestamp": datetime.now().isoformat()
        }
    
    try:
        # Generate a session ID if not provided
        session_id = request.session_id or str(uuid.uuid4())
        
        # Get latest fridge data
        fridge_data = await get_latest_fridge_data()
        
        # Format messages for the API
        messages = format_prompt(request.user_message, fridge_data)
        
        # Make API request to OpenAI
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {OPENAI_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "gpt-4-turbo-preview",  # Use the latest available model
                    "messages": messages,
                    "max_tokens": 500
                }
            )
            
            # Check for errors
            response.raise_for_status()
            result = response.json()
            
            # Extract assistant's message
            assistant_response = result["choices"][0]["message"]["content"]
            
            # Save to chat history
            await save_chat_history(session_id, request.user_message, assistant_response)
            
            return {
                "response": assistant_response,
                "status": "ok",
                "timestamp": datetime.now().isoformat()
            }
            
    except Exception as e:
        logger.error(f"Error getting chat response: {str(e)}")
        return {
            "response": "I'm sorry, I couldn't process your request at this time. Please try again later.",
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        } 