import os
import base64
import logging
from openai import OpenAI
from typing import List, Optional
import json

# Configure logging
logger = logging.getLogger(__name__)

class VisionService:
    """
    Service for handling GPT-4 Vision API interactions
    """
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Vision service with OpenAI API key.
        Uses environment variable if not provided.
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            logger.warning("OPENAI_API_KEY not found. Vision API will not work.")
        
        self.client = OpenAI(api_key=self.api_key) if self.api_key else None

    async def detect_food_items(self, image_base64: str) -> List[str]:
        """
        Detect food items in the provided base64 encoded image using GPT-4 Vision
        
        Args:
            image_base64: Base64 encoded image string
        
        Returns:
            List of detected food items
        """
        if not self.client:
            logger.error("OpenAI client not initialized. Check API key.")
            return []
        
        try:
            # Prepare the image for the API request
            image_url = f"data:image/jpeg;base64,{image_base64}"
            
            # Call OpenAI Vision API
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a smart fridge AI that detects food items in images. "
                                  "Return ONLY a JSON array of food items visible in the image. "
                                  "Be specific, but use common food names."
                    },
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "What food items do you see in this fridge image? "
                                        "Return ONLY a JSON array of food names (e.g., ['apple', 'milk'])."
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": image_url
                                }
                            }
                        ]
                    }
                ],
                max_tokens=300,
            )
            
            # Extract and parse the response
            content = response.choices[0].message.content
            
            # Try to find and extract a JSON array in the response
            try:
                # Look for square brackets in the response
                start_idx = content.find('[')
                end_idx = content.rfind(']') + 1
                
                if start_idx != -1 and end_idx != -1:
                    items_json = content[start_idx:end_idx]
                    return json.loads(items_json)
                
                # If no JSON array format, try to parse the whole response
                return json.loads(content)
            except json.JSONDecodeError:
                # If JSON parsing fails, fallback to simple text parsing
                logger.warning("Failed to parse JSON from Vision API. Falling back to text parsing.")
                lines = content.split('\n')
                items = []
                
                for line in lines:
                    line = line.strip()
                    # Remove common list indicators and quotes
                    for prefix in ['-', '*', '"', "'"]:
                        if line.startswith(prefix):
                            line = line[1:].strip()
                    
                    # Skip empty lines
                    if line and not line.startswith('[') and not line.startswith(']'):
                        items.append(line)
                
                return items
                
        except Exception as e:
            logger.error(f"Error calling GPT-4 Vision API: {str(e)}")
            return []
            
# Create a singleton instance
vision_service = VisionService() 