# Smart Fridge Raspberry Pi System

This project implements a smart fridge monitoring system using Raspberry Pi (or a simulator for testing). The system captures temperature, humidity, and gas levels, takes images of the fridge interior, provides AI-powered vision analysis, and maintains per-user item tracking using SQLite database.

## 🚀 New Features

- **Per-User Item Tracking**: SQLite database integration for tracking items per user
- **Automatic Item Detection**: GPT-4 Vision analyzes images and automatically updates user's item list
- **Smart Item Updates**: Adds new items or updates quantities for existing ones
- **RESTful User Management**: Complete CRUD operations for user items
- **Vision-Based Inventory**: Real-time inventory updates from image analysis

## Components

- **Raspberry Pi Module**: Captures real sensor data and images
- **Simulator**: Emulates sensor data and camera for testing without hardware
- **Backend API**: FastAPI server with SQLite database and AI-powered vision analysis
- **User Item Management**: Per-user item tracking with automatic updates
- **Dashboard**: Web interface for monitoring and interacting with the fridge

## Setting Up

### Requirements

- Python 3.8 or higher
- Required Python packages (install with `pip install -r requirements.txt`)
- OpenAI API key for chat functionality and vision analysis
- SQLite database (automatically created)

### Installation

1. Clone this repository
2. Create a `.env` file in the `backend` directory with your OpenAI API key:
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   FRIDGE_DB_PATH=fridge.db
   ```
3. Install dependencies:
   ```
   pip install -r requirements.txt
   pip install -r backend/requirements.txt
   pip install -r simulator/requirements.txt
   ```

## Running the System

### Starting the Backend Server

```bash
cd backend
uvicorn main:app --reload
```

Or from project root:
```bash
uvicorn backend.main:app --reload
```

This will start the backend server on http://localhost:8000 and automatically create the SQLite database.

### Starting the Simulator

```
python run_simulator.py
```

Optional arguments:
- `--interval`: Monitoring interval in seconds (default: 30)
- `--image-interval`: Image capture interval in seconds (default: 60)
- `--real-api`: Use real API endpoint instead of simulating

## API Endpoints

### User Item Management

#### Get User Items
```
GET /api/user/{username}/items
```

#### Add/Update User Item
```
POST /api/user/{username}/items
```
Request body:
```json
{
  "name": "Apple",
  "quantity": 3,
  "expiry_date": "2025-06-15"
}
```

#### Remove User Item
```
DELETE /api/user/{username}/items/{item_id}
```

### Image Upload with User Tracking
```
POST /api/upload/multipart
```
Form data:
- `data`: JSON with sensor data and user message
- `image`: Image file (optional)
- `username`: Username for item tracking

### Other Endpoints
- `GET /`: Root endpoint
- `GET /api/status`: API status
- `GET /api/fridge-status`: Current fridge status
- `POST /api/chat`: AI chat interface

## Using the Dashboard

1. Open http://localhost:8000 in your web browser
2. The dashboard displays:
   - Current sensor readings (temperature, humidity, gas levels)
   - Latest fridge image with AI analysis
   - Per-user detected food items
   - Item quantity tracking
   - Chat interface to interact with your fridge

## Per-User Item Tracking

The system now maintains separate item lists for each user:

1. **Automatic Detection**: When images are uploaded with a username, detected items are automatically added to that user's list
2. **Smart Updates**: If an item already exists, the quantity is updated; otherwise, a new item is added
3. **Persistent Storage**: All data is stored in SQLite database (`fridge.db`)
4. **Case-Insensitive**: Item matching is case-insensitive for better user experience

### Example Usage:
```python
import requests

# Add item for user 'john'
response = requests.post(
    "http://localhost:8000/api/user/john/items",
    json={"name": "Apple", "quantity": 3}
)

# Get all items for user 'john'
response = requests.get("http://localhost:8000/api/user/john/items")

# Upload image with username (auto-updates items)
files = {
    'data': (None, '{"user_message": "Analyze my fridge"}'),
    'username': (None, 'john'),
    'image': ('fridge.jpg', open('fridge.jpg', 'rb'), 'image/jpeg')
}
response = requests.post("http://localhost:8000/api/upload/multipart", files=files)
```

## Chat Feature

The Smart Fridge includes an AI-powered chat feature that now uses user-specific item data:

- Ask about food items in your personal fridge inventory
- Get recipe suggestions based on your available ingredients
- Get food safety and freshness advice for your items
- Track quantity changes over time

Example questions:
- "What's in my fridge?" (uses your personal item list)
- "How many apples do I have?"
- "What can I make with my ingredients?"
- "Should I buy more milk?"

## Testing

Run the test suite to verify all functionality:

```bash
# Test basic API endpoints
python test_local.py

# Test image upload functionality
python test_image_upload.py

# Test with actual image processing
python test_with_image.py
```

## Database

The system uses SQLite database with the following tables:

### Users Table
- `id`: Primary key
- `username`: Unique username

### Items Table
- `id`: Primary key
- `user_id`: Foreign key to users table
- `name`: Item name
- `quantity`: Item quantity
- `date_added`: When item was first added
- `expiry_date`: Optional expiry date

## Troubleshooting

- **Chat feature not working**: Ensure you have a valid OpenAI API key in the backend/.env file
- **Database errors**: Check write permissions in the backend directory for SQLite database
- **Simulator fails to start**: Check that all required packages are installed
- **Dashboard not loading**: Make sure the backend server is running on port 8000
- **Vision analysis not working**: Verify OpenAI API key has access to GPT-4 Vision
- **Items not updating**: Ensure username is provided in upload requests
