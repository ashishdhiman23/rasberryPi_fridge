# Smart Fridge API Documentation

## Overview

This document provides comprehensive API documentation for the Smart Fridge system. The API allows mobile applications, web dashboards, and other clients to interact with the Smart Fridge backend, access sensor data, detect food items, manage per-user item tracking, and chat with the AI assistant.

**Production Base URL**: `https://smart-fridge-backend.onrender.com/api`
**Local Development Base URL**: `http://localhost:8000/api`

## 🆕 New Features

- **Per-User Item Tracking**: SQLite database with user-specific item lists
- **Automatic Item Detection**: GPT-4 Vision analysis with database integration
- **Smart Item Updates**: Automatic quantity updates for existing items
- **RESTful User Management**: Complete CRUD operations for user items

## System Architecture

The Smart Fridge system consists of the following components:

1. **Raspberry Pi Hardware**: Physical implementation with real sensors and camera
2. **Simulator**: Software that mimics the Raspberry Pi's functionality for testing
3. **Backend API**: FastAPI service with SQLite database and AI-powered vision analysis
4. **User Item Management**: Per-user item tracking with automatic updates
5. **Frontend Dashboard**: Web interface for visualization and interaction
6. **Mobile App**: Native mobile application (future development)

## API Endpoints

### Status Endpoints

#### Get API Status

Check if the API is online and retrieve basic system information.

**Endpoint**: `GET /status`

**Response**:
```json
{
  "status": "online",
  "message": "API is running",
  "timestamp": "2025-06-02T15:54:22.182387",
  "server_info": {
    "database": "SQLite",
    "python_version": "3.11.11"
  }
}
```

### User Item Management Endpoints

#### Get User Items

Retrieve all items for a specific user.

**Endpoint**: `GET /api/user/{username}/items`

**Response**:
```json
[
  {
    "id": 1,
    "name": "Apple",
    "quantity": 5,
    "date_added": "2025-06-02 10:30:00",
    "expiry_date": "2025-06-10"
  },
  {
    "id": 2,
    "name": "Milk",
    "quantity": 1,
    "date_added": "2025-06-02 10:35:00",
    "expiry_date": null
  }
]
```

**Error Responses**:
- `404`: User not found

#### Add or Update User Item

Add a new item or update quantity if item already exists (case-insensitive).

**Endpoint**: `POST /api/user/{username}/items`

**Request Body**:
```json
{
  "name": "Apple",
  "quantity": 3,
  "expiry_date": "2025-06-10"
}
```

**Response**:
```json
{
  "id": 1,
  "name": "Apple",
  "quantity": 8,
  "date_added": "2025-06-02 10:30:00",
  "expiry_date": "2025-06-10"
}
```

**Notes**:
- If item exists, quantities are added together
- User is automatically created if doesn't exist
- Item name matching is case-insensitive

#### Remove User Item

Remove a specific item from a user's list.

**Endpoint**: `DELETE /api/user/{username}/items/{item_id}`

**Response**:
```json
{
  "message": "Item removed successfully"
}
```

**Error Responses**:
- `404`: User or item not found

### Fridge Data Endpoints

#### Get Fridge Status

Retrieve current fridge status including temperature, humidity, gas levels, and detected food items.

**Endpoint**: `GET /fridge-status`

**Response**:
```json
{
  "temp": 4.2,
  "humidity": 52.3,
  "gas": 125,
  "items": ["milk", "eggs", "cheese", "yogurt", "leftovers"],
  "priority": ["milk (expires soon)", "leftovers (3d old)"],
  "analysis": {
    "freshness": "All items appear fresh",
    "safety": "Temperature is in the safe range (2-5°C)",
    "fill_level": "Fridge is 60% full",
    "recommendations": "Consider consuming milk soon"
  },
  "timestamp": "2025-06-02T16:30:45.123456"
}
```

#### Upload Sensor Data and Images with User Tracking

Upload sensor readings and fridge images with automatic user item tracking. This endpoint uses `multipart/form-data` format to handle JSON data, image files, and user identification.

**Endpoint**: `POST /upload/multipart`

**Request Parameters**:
- `data` (form field): JSON string containing sensor readings and user message
  ```json
  {
    "user_message": "Analyze my fridge contents",
    "temp": 4.2,
    "humidity": 52.3,
    "gas": 125,
    "timestamp": "2025-06-02T16:40:00.000000"
  }
  ```
- `image` (file, optional): Image file of fridge contents (JPEG or PNG)
- `username` (form field, required): Username for item tracking

**Response**:
```json
{
  "status": "success",
  "message": "Data received and processed with AI vision",
  "timestamp": "2025-06-02T16:40:05.789012",
  "image_processed": true,
  "food_items": ["milk", "eggs", "apple"],
  "temperature_status": "normal",
  "vision_confidence": "high",
  "analysis": "The fridge contains fresh items including milk, eggs, and apples...",
  "guardrail": {
    "is_food_likely": true,
    "food_confidence": 0.95,
    "method": "gpt_vision_analysis"
  }
}
```

**Important Notes**:
- **Username is required** for item tracking
- Detected food items are automatically added to the user's item list
- If items already exist, quantities are updated
- Vision analysis requires valid OpenAI API key with GPT-4 Vision access

**Error Responses**:
- `400`: Username is required
- `500`: Vision analysis failed

### AI Assistant Endpoints

#### Chat with Fridge

Send messages to the AI assistant to ask questions about fridge contents, get recipe suggestions, or inquire about food safety. The AI now uses user-specific item data.

**Endpoint**: `POST /chat`

**Request Body**:
```json
{
  "user_message": "What can I make with the ingredients in my fridge?",
  "session_id": "optional-session-id-for-conversation-tracking"
}
```

**Response**:
```json
{
  "response": "Based on your current items (milk, eggs, cheese, and apples), you could make a delicious omelet or apple pancakes. You have 5 apples and fresh eggs, perfect for breakfast!",
  "status": "ok",
  "timestamp": "2025-06-02T16:35:12.654321",
  "session_id": "generated-or-provided-session-id"
}
```

## Data Models

### User Item Model

| Field | Type | Description |
|-------|------|-------------|
| id | integer | Unique item identifier |
| name | string | Item name |
| quantity | integer | Item quantity |
| date_added | string | ISO 8601 timestamp when item was first added |
| expiry_date | string (optional) | ISO 8601 date when item expires |

### Sensor Data

| Field | Type | Description |
|-------|------|-------------|
| temp | float | Temperature in Celsius |
| humidity | float | Humidity percentage |
| gas | float | Gas level in PPM |
| timestamp | string | ISO 8601 timestamp |

### Chat Request

| Field | Type | Description |
|-------|------|-------------|
| user_message | string | Message from the user |
| session_id | string (optional) | Session ID for conversation tracking |

### Chat Response

| Field | Type | Description |
|-------|------|-------------|
| response | string | Response from the AI assistant |
| status | string | Status of the request (ok/error) |
| timestamp | string | ISO 8601 timestamp |
| session_id | string (optional) | Session ID for conversation tracking |

## Database Schema

### Users Table
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL
);
```

### Items Table
```sql
CREATE TABLE items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    quantity INTEGER DEFAULT 1,
    date_added TEXT DEFAULT CURRENT_TIMESTAMP,
    expiry_date TEXT,
    FOREIGN KEY(user_id) REFERENCES users(id)
);
```

## Error Handling

All API endpoints return appropriate HTTP status codes:
- 200: Success
- 400: Bad request (invalid parameters)
- 404: Resource not found
- 500: Server error

Error responses include a JSON object with details:
```json
{
  "status": "error",
  "message": "Error processing upload: Username is required",
  "timestamp": "2025-06-02T16:45:00.000000"
}
```

## Implementation Examples

### Python Integration

```python
import requests

# Add item for user
response = requests.post(
    "http://localhost:8000/api/user/john/items",
    json={"name": "Apple", "quantity": 3}
)

# Get user items
response = requests.get("http://localhost:8000/api/user/john/items")
items = response.json()

# Upload image with username
files = {
    'data': (None, '{"user_message": "Analyze my fridge"}'),
    'username': (None, 'john'),
    'image': ('fridge.jpg', open('fridge.jpg', 'rb'), 'image/jpeg')
}
response = requests.post("http://localhost:8000/api/upload/multipart", files=files)
```

### cURL Examples

```bash
# Get user items
curl -X GET "http://localhost:8000/api/user/john/items"

# Add item
curl -X POST "http://localhost:8000/api/user/john/items" \
  -H "Content-Type: application/json" \
  -d '{"name": "Apple", "quantity": 3}'

# Upload with image and username
curl -X POST "http://localhost:8000/api/upload/multipart" \
  -F "username=john" \
  -F "data={\"user_message\": \"Analyze my fridge\"}" \
  -F "image=@fridge.jpg"
```

## Migration from Previous Version

If upgrading from a version without user tracking:

1. The SQLite database will be automatically created on first run
2. Previous global item lists are not migrated - users need to re-scan their fridges
3. All upload requests now require a `username` parameter
4. Chat responses now use user-specific data instead of global data

## Testing

The API includes test scripts for verification:

```bash
# Test basic user item endpoints
python test_local.py

# Test image upload functionality  
python test_image_upload.py

# Test with actual image processing
python test_with_image.py
```

## Development and Testing

### Environment Setup

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/your-org/smart-fridge.git
   cd smart-fridge
   ```

2. **Set Up Virtual Environment**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .\.venv\Scripts\activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment Variables**:
   Create a `.env` file with the following variables:
   ```
   OPENAI_API_KEY=your_openai_api_key
   ALLOWED_ORIGINS=http://localhost:3000,https://your-app-domain.com
   ```

### Running the Simulator

The Smart Fridge simulator allows testing without physical hardware:

```bash
# Run with default settings
python run_simulator.py

# Run with custom intervals and real API connection
python run_simulator.py --interval 30 --image-interval 60 --real-api
```

### Required Python Packages

Make sure to install these packages:
- `fastapi`
- `uvicorn`
- `python-dotenv`
- `httpx`
- `python-multipart`
- `pillow`
- `pydantic`
- `schedule`

## Troubleshooting

1. **404 Errors**: Ensure you're using the correct endpoint paths. The base URL is `https://smart-fridge-backend.onrender.com/api` and all endpoints should be appended to this.

2. **Upload Failures**: For multipart uploads, ensure that:
   - The `data` field contains valid JSON
   - Any images are properly formatted and not too large (< 5MB recommended)

3. **Service Unavailability**: The backend service is hosted on Render's free tier, which can occasionally experience cold starts. If you receive a "Bad Gateway" error, try again after a minute.

4. **Simulator Connection Issues**: If the simulator reports "Upload failed: HTTP 404", ensure that the API URL in `simulator/config.py` matches the backend endpoint.

## Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Render Deployment Guide](https://render.com/docs/deploy-fastapi)
- [OpenAI API Reference](https://platform.openai.com/docs/api-reference)

## Contact

For questions or support, please contact the development team or create an issue in the GitHub repository.

---

Last updated: June 2, 2025 