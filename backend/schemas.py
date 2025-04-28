from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from datetime import datetime

class SensorData(BaseModel):
    """Schema for sensor data from the Raspberry Pi"""
    temp: float = Field(..., description="Temperature in Celsius", example=4.2)
    humidity: float = Field(..., description="Humidity percentage", example=62)
    gas: int = Field(..., description="Gas level in ppm", example=190)
    image_base64: str = Field(..., description="Base64 encoded fridge image")

class FridgeStatusResponse(BaseModel):
    """Schema for the fridge status response"""
    status: str = Field(..., description="API status", example="ok")
    timestamp: datetime = Field(..., description="Timestamp of the data")
    temp: float = Field(..., description="Temperature in Celsius")
    humidity: float = Field(..., description="Humidity percentage")
    gas: int = Field(..., description="Gas level in ppm")
    items: List[str] = Field(..., description="Detected food items")
    ai_response: Optional[str] = Field(None, description="AI response message")
    priority: List[str] = Field(["safety", "freshness", "recipes"], 
                                description="Priority order for analysis")
    analysis: Dict[str, str] = Field(..., description="AI analysis results")

class VisionResponse(BaseModel):
    """Schema for the GPT-4 Vision API response"""
    items: List[str] = Field(..., description="Detected food items")

class AgentAnalysis(BaseModel):
    """Schema for the FridgeAgent analysis result"""
    ai_response: str = Field(..., description="AI response message")
    priority: List[str] = Field(..., description="Priority order")
    analysis: Dict[str, str] = Field(..., description="Analysis by category") 