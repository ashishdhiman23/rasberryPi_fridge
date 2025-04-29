"""
Chat agent module for Smart Fridge Simulator.
Enables users to "chat with their fridge" using GPT-4/GPT-4 Vision.
"""
import os
import json
import base64
import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, List, Union, Any

import httpx
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)

# Constants
DEFAULT_SYSTEM_PROMPT = """
You are a smart fridge assistant. You help the user make decisions based on the 
current temperature, humidity, gas levels, and visible food items in their fridge.
Be helpful, concise, and practical. If the temperature is outside of safe range (1-5°C),
warn the user. For food items, consider freshness based on when they were last seen.
"""

FALLBACK_RESPONSE = "I'm sorry, I couldn't process your request at this time. Please try again later."

# Get OpenAI API key from environment
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    logger.warning("OPENAI_API_KEY not found in environment variables")

class ChatAgent:
    """Agent that enables chat interaction with the smart fridge using GPT-4."""
    
    def __init__(self, data_dir: str = "simulator", 
                 system_prompt: Optional[str] = None):
        """
        Initialize the chat agent.
        
        Args:
            data_dir: Directory where fridge data and images are stored
            system_prompt: Custom system prompt to use instead of the default
        """
        self.data_dir = Path(data_dir)
        self.images_dir = self.data_dir / "mock_images"
        self.data_file = self.data_dir / "last_upload.json"
        self.api_response_file = self.data_dir / "last_api_response.json"
        self.system_prompt = system_prompt or DEFAULT_SYSTEM_PROMPT
        
        # Create a history file if it doesn't exist
        self.history_file = self.data_dir / "chat_history.json"
        if not self.history_file.exists():
            with open(self.history_file, "w") as f:
                json.dump({"sessions": {}}, f)
    
    def _get_latest_fridge_data(self) -> Dict[str, Any]:
        """
        Get the latest fridge data, combining sensor readings and last seen food items.
        
        Returns:
            dict: Combined fridge data
        """
        try:
            # Read sensor data from last_upload.json
            if self.data_file.exists():
                with open(self.data_file, "r") as f:
                    sensor_data = json.load(f)
            else:
                logger.warning(f"Data file {self.data_file} not found")
                sensor_data = {"temp": None, "humidity": None, "gas": None}
            
            # Read food items from API response if available
            last_seen_items = {}
            if self.api_response_file.exists():
                try:
                    with open(self.api_response_file, "r") as f:
                        api_data = json.load(f)
                    
                    # Look for food items in the API response
                    if "food_items" in api_data:
                        for item in api_data["food_items"]:
                            # Calculate days since last seen
                            if "detected_at" in item:
                                detected_time = datetime.fromisoformat(item["detected_at"])
                                days_ago = (datetime.now() - detected_time).days
                                last_seen_items[item["name"]] = days_ago
                            else:
                                last_seen_items[item["name"]] = 0
                except (json.JSONDecodeError, KeyError) as e:
                    logger.error(f"Error parsing API response: {str(e)}")
            
            # Combine the data
            fridge_data = {
                "temp": sensor_data.get("temp"),
                "humidity": sensor_data.get("humidity"),
                "gas": sensor_data.get("gas"),
                "last_seen": last_seen_items,
                "timestamp": sensor_data.get("timestamp", datetime.now().isoformat())
            }
            
            return fridge_data
        
        except Exception as e:
            logger.error(f"Error getting fridge data: {str(e)}")
            return {
                "temp": None, 
                "humidity": None, 
                "gas": None,
                "last_seen": {},
                "timestamp": datetime.now().isoformat()
            }
    
    def _get_latest_image(self) -> Optional[str]:
        """
        Get the latest fridge image as a base64 string.
        
        Returns:
            str: Base64 encoded image or None if no image is found
        """
        try:
            # Find the most recent image file (not starting with IMG- which are source images)
            image_files = [f for f in self.images_dir.glob("fridge_*.jpg") if f.is_file()]
            
            if not image_files:
                logger.warning("No fridge images found")
                return None
            
            # Sort by creation time, newest first
            latest_image = max(image_files, key=lambda f: f.stat().st_mtime)
            
            # Read and encode the image
            with open(latest_image, "rb") as img_file:
                image_data = img_file.read()
                base64_image = base64.b64encode(image_data).decode("utf-8")
                logger.info(f"Found latest image: {latest_image.name}")
                return base64_image
        
        except Exception as e:
            logger.error(f"Error getting latest image: {str(e)}")
            return None
    
    def _format_prompt(self, user_message: str, include_image: bool = False) -> Dict:
        """
        Format the prompt for the GPT-4 API.
        
        Args:
            user_message: The user's message
            include_image: Whether to include the latest fridge image
            
        Returns:
            dict: Formatted messages for the API
        """
        fridge_data = self._get_latest_fridge_data()
        
        # Format the fridge status text
        food_items_text = ""
        if fridge_data["last_seen"]:
            food_items = []
            for item, days in fridge_data["last_seen"].items():
                suffix = "d ago" if days > 0 else "today"
                days_text = days if days > 0 else ""
                food_items.append(f"{item} ({days_text}{suffix})")
            food_items_text = "- Food items seen: " + ", ".join(food_items)
        else:
            food_items_text = "- No food items detected"
        
        fridge_status = f"""
Here is my latest fridge status:
- Temperature: {fridge_data['temp'] if fridge_data['temp'] is not None else 'Unknown'} °C
- Humidity: {fridge_data['humidity'] if fridge_data['humidity'] is not None else 'Unknown'}%
- Gas Level: {fridge_data['gas'] if fridge_data['gas'] is not None else 'Unknown'} PPM
{food_items_text}

User: "{user_message}"
"""
        
        # Create messages array
        messages = [
            {"role": "system", "content": self.system_prompt},
        ]
        
        # Add image if requested
        if include_image:
            base64_image = self._get_latest_image()
            if base64_image:
                messages.append({
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Here is the current image of my fridge interior:"},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        },
                        {"type": "text", "text": fridge_status}
                    ]
                })
            else:
                # No image available, just use text
                messages.append({
                    "role": "user",
                    "content": fridge_status
                })
        else:
            # Text only prompt
            messages.append({
                "role": "user",
                "content": fridge_status
            })
        
        return messages
    
    async def save_chat_history(self, session_id: str, 
                               user_message: str, 
                               assistant_response: str) -> None:
        """
        Save chat history to a JSON file.
        
        Args:
            session_id: Unique session identifier
            user_message: User's message
            assistant_response: Assistant's response
        """
        try:
            if self.history_file.exists():
                with open(self.history_file, "r") as f:
                    history = json.load(f)
            else:
                history = {"sessions": {}}
            
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
            with open(self.history_file, "w") as f:
                json.dump(history, f, indent=2)
                
        except Exception as e:
            logger.error(f"Error saving chat history: {str(e)}")
    
    async def get_chat_response(self, 
                               user_message: str,
                               session_id: Optional[str] = None,
                               include_image: bool = False,
                               model: str = "gpt-4-1106-preview") -> Dict[str, str]:
        """
        Get a response from GPT-4 for the user's message.
        
        Args:
            user_message: The user's message
            session_id: Optional session identifier for tracking conversations
            include_image: Whether to include the latest fridge image
            model: GPT model to use (use gpt-4-vision-preview for images)
            
        Returns:
            dict: Response with status and text
        """
        if not OPENAI_API_KEY:
            return {
                "response": "OpenAI API key not configured. Please set the OPENAI_API_KEY environment variable.",
                "status": "error"
            }
        
        # Use vision model if image is included
        if include_image:
            model = "gpt-4-vision-preview"
            
        # Format messages for the API
        messages = self._format_prompt(user_message, include_image)
        
        try:
            # Make API request
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {OPENAI_API_KEY}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": model,
                        "messages": messages,
                        "max_tokens": 500
                    }
                )
                
                # Check for errors
                response.raise_for_status()
                result = response.json()
                
                # Extract assistant's message
                assistant_response = result["choices"][0]["message"]["content"]
                
                # Save to chat history if session_id provided
                if session_id:
                    await self.save_chat_history(session_id, user_message, assistant_response)
                
                return {
                    "response": assistant_response,
                    "status": "ok"
                }
                
        except Exception as e:
            logger.error(f"Error getting chat response: {str(e)}")
            return {
                "response": FALLBACK_RESPONSE,
                "status": "error",
                "error": str(e)
            }


# Simple test function
async def test_chat_agent():
    """Test the chat agent with a sample question."""
    agent = ChatAgent()
    response = await agent.get_chat_response(
        "What food do I have and can I make a salad?",
        include_image=True
    )
    print(json.dumps(response, indent=2))


if __name__ == "__main__":
    import asyncio
    asyncio.run(test_chat_agent()) 