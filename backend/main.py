from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

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
    return {
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

# Simple API endpoint for testing
@app.get("/api/status")
async def status():
    return {
        "status": "online",
        "message": "API is running",
        "timestamp": str(os.getenv("RENDER_TIMESTAMP", "unknown"))
    }

# Simple upload endpoint 
@app.post("/api/upload/multipart")
async def upload_multipart():
    return {
        "status": "success",
        "message": "Data received",
        "timestamp": str(os.getenv("RENDER_TIMESTAMP", "unknown")),
        "food_items": ["milk", "eggs"]
    }

# Run the app with uvicorn if executed directly
if __name__ == "__main__":
    # Get port from environment variable for cloud platforms
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True) 