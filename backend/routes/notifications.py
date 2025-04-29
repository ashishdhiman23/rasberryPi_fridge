"""
Real-time notifications API for Smart Fridge system.
Provides endpoints for getting alerts and notifications.
"""
from fastapi import APIRouter, HTTPException
import json
import os
import logging
from typing import Dict, List, Optional
from datetime import datetime
from pydantic import BaseModel

# Configure logging
logger = logging.getLogger(__name__)

# Path to store notifications data
NOTIFICATIONS_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "notifications.json")

# Create router
router = APIRouter()

# Models
class Notification(BaseModel):
    """Model for a notification"""
    id: str
    type: str  # "alert", "info", "expiry"
    title: str
    message: str
    created_at: str
    read: bool = False
    priority: int  # 1 (high) to 5 (low)
    

class NotificationResponse(BaseModel):
    """Model for notification response"""
    notifications: List[Notification]
    unread_count: int
    
    
# Helper functions
def _load_notifications() -> List[Dict]:
    """Load notifications from file"""
    try:
        if os.path.exists(NOTIFICATIONS_PATH):
            with open(NOTIFICATIONS_PATH, "r") as f:
                return json.load(f)
        else:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(NOTIFICATIONS_PATH), exist_ok=True)
            return []
    except Exception as e:
        logger.error(f"Error loading notifications: {str(e)}")
        return []


def _save_notifications(notifications: List[Dict]) -> None:
    """Save notifications to file"""
    try:
        with open(NOTIFICATIONS_PATH, "w") as f:
            json.dump(notifications, f, indent=2)
    except Exception as e:
        logger.error(f"Error saving notifications: {str(e)}")


def _generate_notification_id() -> str:
    """Generate a unique notification ID"""
    import uuid
    return str(uuid.uuid4())


@router.get("/notifications", response_model=NotificationResponse, summary="Get user notifications")
async def get_notifications():
    """
    Retrieve notifications for the user
    
    Returns a list of notifications with unread count
    """
    try:
        notifications = _load_notifications()
        unread_count = sum(1 for n in notifications if not n.get("read", False))
        
        return {
            "notifications": notifications,
            "unread_count": unread_count
        }
    except Exception as e:
        logger.error(f"Error retrieving notifications: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving notifications: {str(e)}")


@router.post("/notifications/read/{notification_id}", summary="Mark notification as read")
async def mark_notification_read(notification_id: str):
    """
    Mark a notification as read
    
    Args:
        notification_id: The ID of the notification to mark as read
    """
    try:
        notifications = _load_notifications()
        
        for notification in notifications:
            if notification.get("id") == notification_id:
                notification["read"] = True
                break
        
        _save_notifications(notifications)
        
        return {"status": "success"}
    except Exception as e:
        logger.error(f"Error marking notification as read: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error marking notification as read: {str(e)}")


@router.post("/notifications/read-all", summary="Mark all notifications as read")
async def mark_all_notifications_read():
    """Mark all notifications as read"""
    try:
        notifications = _load_notifications()
        
        for notification in notifications:
            notification["read"] = True
        
        _save_notifications(notifications)
        
        return {"status": "success"}
    except Exception as e:
        logger.error(f"Error marking all notifications as read: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error marking all notifications as read: {str(e)}")


# Function to be called from other modules to create notifications
def create_notification(type: str, title: str, message: str, priority: int = 3) -> None:
    """
    Create a new notification
    
    Args:
        type: The notification type ("alert", "info", "expiry")
        title: The notification title
        message: The notification message
        priority: Priority level (1-5, where 1 is highest)
    """
    try:
        notifications = _load_notifications()
        
        # Create new notification
        notification = {
            "id": _generate_notification_id(),
            "type": type,
            "title": title,
            "message": message,
            "created_at": datetime.now().isoformat(),
            "read": False,
            "priority": priority
        }
        
        # Add to list (at the beginning)
        notifications.insert(0, notification)
        
        # Keep only the most recent 50 notifications
        if len(notifications) > 50:
            notifications = notifications[:50]
        
        _save_notifications(notifications)
        
        logger.info(f"Created notification: {title}")
    except Exception as e:
        logger.error(f"Error creating notification: {str(e)}") 