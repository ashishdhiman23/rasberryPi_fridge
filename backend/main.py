from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
from dotenv import load_dotenv

from routes.upload import router as upload_router
from routes.status import router as status_router
from routes.notifications import router as notifications_router
from routes.chat import router as chat_router

# Load environment variables from .env file
load_dotenv()

# Verify OpenAI API key is available
if not os.getenv("OPENAI_API_KEY"):
    print("WARNING: OPENAI_API_KEY not found in environment variables.")
    print("The Smart Fridge AI features will not work properly.")
    print("Please set up your .env file with a valid API key.")

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
    allow_origins=allowed_origins,  # Use environment variable value
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(upload_router, prefix="/api")
app.include_router(status_router, prefix="/api")
app.include_router(notifications_router, prefix="/api")
app.include_router(chat_router, prefix="/api")

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

# Run the app with uvicorn if executed directly
if __name__ == "__main__":
    # Get port from environment variable for cloud platforms
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True) 