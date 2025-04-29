"""
Expiration Tracking Agent for Smart Fridge system.
Tracks and predicts expiration dates for food items.
"""
import logging
import os
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from openai import OpenAI

# Configure logging
logger = logging.getLogger(__name__)

# Path to store expiration data
EXPIRATION_DATA_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "expiration_data.json")


class ExpirationTracker:
    """Agent for tracking food item expiration dates"""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4"):
        """Initialize Expiration Tracker with OpenAI API key"""
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            logger.warning("OPENAI_API_KEY not found. Expiration tracking will use defaults only.")
        
        self.client = OpenAI(api_key=self.api_key) if self.api_key else None
        self.model = model
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(EXPIRATION_DATA_PATH), exist_ok=True)
        
        # Load existing expiration data
        self.expiration_data = self._load_expiration_data()
    
    def _load_expiration_data(self) -> Dict:
        """Load expiration data from file"""
        try:
            if os.path.exists(EXPIRATION_DATA_PATH):
                with open(EXPIRATION_DATA_PATH, "r") as f:
                    return json.load(f)
            return {}
        except Exception as e:
            logger.error(f"Error loading expiration data: {str(e)}")
            return {}
    
    def _save_expiration_data(self) -> None:
        """Save expiration data to file"""
        try:
            with open(EXPIRATION_DATA_PATH, "w") as f:
                json.dump(self.expiration_data, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving expiration data: {str(e)}")
    
    async def update_item_expiration(self, item: str, first_seen: Optional[str] = None) -> None:
        """
        Update the expiration data for a food item
        
        Args:
            item: The food item name
            first_seen: ISO format datetime string when the item was first detected
        """
        now = datetime.now()
        
        # If item already exists, update its last_seen date
        if item in self.expiration_data:
            self.expiration_data[item]["last_seen"] = now.isoformat()
        else:
            # If item is new, add it with default expiration estimate
            expiry_days = await self._estimate_expiry_days(item)
            
            self.expiration_data[item] = {
                "first_seen": first_seen or now.isoformat(),
                "last_seen": now.isoformat(),
                "estimated_expiry_days": expiry_days,
                "estimated_expiry_date": (now + timedelta(days=expiry_days)).isoformat()
            }
        
        # Save updated data
        self._save_expiration_data()
    
    async def _estimate_expiry_days(self, item: str) -> int:
        """
        Estimate the number of days until a food item expires
        
        Args:
            item: The food item name
            
        Returns:
            int: Estimated days until expiration
        """
        # Default expiration days for common food types
        default_expiry = {
            "milk": 7,
            "yogurt": 14,
            "cheese": 21,
            "eggs": 21,
            "butter": 30,
            "apple": 14,
            "banana": 5,
            "orange": 14,
            "tomato": 7,
            "lettuce": 7,
            "cucumber": 7,
            "carrot": 21,
            "chicken": 3,
            "beef": 3,
            "fish": 2,
            "leftover": 3,
            "juice": 7,
            "soda": 180,
            "bread": 7,
            "cake": 4
        }
        
        # Try to find item in defaults first (case insensitive partial match)
        item_lower = item.lower()
        for key, days in default_expiry.items():
            if key in item_lower or item_lower in key:
                return days
                
        # If item not found in defaults and we have OpenAI access, ask the model
        if self.client:
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a food safety expert. Provide the typical refrigerator shelf life in days for a food item. Respond with ONLY a number, no explanation or additional text."
                        },
                        {
                            "role": "user",
                            "content": f"How many days does '{item}' typically last in a refrigerator? Respond with just a number."
                        }
                    ],
                    max_tokens=10,
                    temperature=0
                )
                
                # Try to parse the response as an integer
                try:
                    days = int(response.choices[0].message.content.strip())
                    return days
                except ValueError:
                    # If parsing fails, return default
                    return 7
                    
            except Exception as e:
                logger.error(f"Error estimating expiry days with OpenAI: {str(e)}")
                
        # Default if everything else fails
        return 7
    
    async def process_items(self, items: List[str]) -> None:
        """
        Process a list of food items to update their tracking
        
        Args:
            items: List of food items detected in the fridge
        """
        if not items:
            return
            
        # Update tracking for each item
        for item in items:
            await self.update_item_expiration(item)
        
        # Mark items as removed if they're not seen in this update
        now = datetime.now()
        for existing_item in list(self.expiration_data.keys()):
            if existing_item not in items:
                # If item was last seen more than 24 hours ago, assume it's removed
                last_seen = datetime.fromisoformat(self.expiration_data[existing_item]["last_seen"])
                if (now - last_seen).total_seconds() > 86400:  # 24 hours in seconds
                    if "removed_date" not in self.expiration_data[existing_item]:
                        self.expiration_data[existing_item]["removed_date"] = now.isoformat()
        
        # Save changes
        self._save_expiration_data()
    
    def get_expiring_soon(self, days_threshold: int = 3) -> List[Dict]:
        """
        Get items that are expiring soon
        
        Args:
            days_threshold: Number of days to consider as "expiring soon"
            
        Returns:
            List of items with expiration info
        """
        now = datetime.now()
        expiring_soon = []
        
        for item, data in self.expiration_data.items():
            # Skip items that have been removed
            if "removed_date" in data:
                continue
                
            # Calculate days until expiration
            expiry_date = datetime.fromisoformat(data["estimated_expiry_date"])
            days_until_expiry = (expiry_date - now).days
            
            if days_until_expiry <= days_threshold:
                expiring_soon.append({
                    "item": item,
                    "days_remaining": days_until_expiry,
                    "expiry_date": data["estimated_expiry_date"]
                })
        
        # Sort by days remaining
        expiring_soon.sort(key=lambda x: x["days_remaining"])
        return expiring_soon
    
    async def get_expiration_analysis(self, items: List[str]) -> Dict:
        """
        Get analysis of food expiration status
        
        Args:
            items: Current items in the fridge
            
        Returns:
            Dict with expiration analysis
        """
        # Process the items first
        await self.process_items(items)
        
        # Get items expiring soon
        expiring_soon = self.get_expiring_soon()
        
        # Build the analysis message
        if not expiring_soon:
            message = "✅ All items are fresh! No food needs immediate attention."
        else:
            message = "⏰ Expiring Soon:\n"
            for item in expiring_soon:
                days = item["days_remaining"]
                if days <= 0:
                    message += f"🚨 {item['item']} - Expired!\n"
                elif days == 1:
                    message += f"🟡 {item['item']} - Expires today!\n"
                else:
                    message += f"🟡 {item['item']} - {days} days remaining\n"
            
            message += "\nConsider using these items soon to avoid waste."
        
        return {"expiration": message}


# Create a singleton instance
expiration_tracker = ExpirationTracker() 