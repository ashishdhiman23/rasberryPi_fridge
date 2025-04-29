"""
API routes for the Smart Fridge Simulator.
Provides endpoints for interacting with the fridge, including the chat feature.
"""
import uuid
from typing import Optional, Dict, Any
from datetime import datetime

from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, Field

from simulator.chat_agent import ChatAgent

# Initialize FastAPI app
app = FastAPI(
    title="Smart Fridge API",
    description="API for interacting with the Smart Fridge Simulator",
    version="1.0.0"
)

# Initialize chat agent
chat_agent = ChatAgent()

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