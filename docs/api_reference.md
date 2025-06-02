# Smart Fridge API Reference

This document provides a comprehensive reference for the Smart Fridge API endpoints, request/response formats, and database schema.

## Base URLs

**Local Development**: `http://localhost:8000/api`
**Production**: `https://smart-fridge-backend.onrender.com/api`

## Authentication

Currently, the API does not require authentication. Future versions may implement token-based authentication for production deployments.

## Endpoints

### User Item Management

#### Get User Items

```
GET /api/user/{username}/items
```

Retrieves all items for a specific user.

**Path Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| username | String | Yes | Username to retrieve items for |

**Response:**
```json
[
  {
    "id": 1,
    "name": "Apple",
    "quantity": 5,
    "date_added": "2025-06-02 10:30:00",
    "expiry_date": "2025-06-10"
  }
]
```

**Error Responses:**
| Status Code | Description |
|-------------|-------------|
| 404 | User not found |

#### Add or Update User Item

```
POST /api/user/{username}/items
Content-Type: application/json
```

Adds a new item or updates quantity if item already exists (case-insensitive).

**Path Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| username | String | Yes | Username to add item for |

**Request Body:**
```json
{
  "name": "Apple",
  "quantity": 3,
  "expiry_date": "2025-06-15"
}
```

**Request Fields:**
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| name | String | Yes | Name of the item |
| quantity | Integer | No | Quantity to add (default: 1) |
| expiry_date | String | No | ISO 8601 date when item expires |

**Response:**
```json
{
  "id": 1,
  "name": "Apple", 
  "quantity": 8,
  "date_added": "2025-06-02 10:30:00",
  "expiry_date": "2025-06-15"
}
```

**Notes:**
- User is automatically created if doesn't exist
- If item exists, quantities are added together
- Item name matching is case-insensitive

#### Remove User Item

```
DELETE /api/user/{username}/items/{item_id}
```

Removes a specific item from a user's inventory.

**Path Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| username | String | Yes | Username to remove item from |
| item_id | Integer | Yes | ID of item to remove |

**Response:**
```json
{
  "message": "Item removed successfully"
}
```

**Error Responses:**
| Status Code | Description |
|-------------|-------------|
| 404 | User or item not found |

### Data Upload

#### Upload Sensor Data and Images with User Tracking

```
POST /api/upload/multipart
Content-Type: multipart/form-data
```

Uploads sensor data and images with automatic user item tracking through AI vision analysis.

**Form Data Parameters:**
| Field Name | Type | Required | Description |
|------------|------|----------|-------------|
| username | String | Yes | Username for item tracking |
| data | String | Yes | JSON string with sensor data and user message |
| image | File | No | Image file (JPEG/PNG) of fridge interior |

**Data Field JSON Structure:**
```json
{
  "user_message": "Analyze my fridge contents",
  "temp": 4.2,
  "humidity": 45.7,
  "gas": 12.3,
  "timestamp": "2025-06-02T14:30:45Z"
}
```

**Example Request:**
```bash
curl -X POST http://localhost:8000/api/upload/multipart \
  -F "username=john" \
  -F "data={\"user_message\": \"Analyze my fridge\", \"temp\": 4.2}" \
  -F "image=@fridge_image.jpg"
```

**Response:**
```json
{
  "status": "success",
  "message": "Data received and processed with AI vision",
  "timestamp": "2025-06-02T14:30:47Z",
  "image_processed": true,
  "food_items": ["milk", "eggs", "apple"],
  "temperature_status": "normal",
  "vision_confidence": "high",
  "analysis": "The fridge contains fresh items...",
  "guardrail": {
    "is_food_likely": true,
    "food_confidence": 0.95
  }
}
```

**Important Notes:**
- Detected food items are automatically added to the user's item list
- Existing items have quantities updated
- Vision analysis requires OpenAI API key with GPT-4 Vision access

**Error Responses:**
| Status Code | Description |
|-------------|-------------|
| 400 | Username is required or invalid data format |
| 500 | Vision analysis failed or server error |

### Data Retrieval

#### Get Fridge Status

```
GET /api/fridge-status
```

Retrieves current fridge status including sensor readings and detected items.

**Response:**
```json
{
  "temp": 4.2,
  "humidity": 52.3,
  "gas": 125,
  "items": ["milk", "eggs", "cheese"],
  "priority": ["milk (expires soon)"],
  "analysis": {
    "freshness": "All items appear fresh",
    "safety": "Temperature is in safe range",
    "recommendations": "Consider consuming milk soon"
  },
  "timestamp": "2025-06-02T16:30:45Z"
}
```

#### Get API Status

```
GET /api/status
```

Returns API health status and system information.

**Response:**
```json
{
  "status": "online",
  "message": "API is running",
  "timestamp": "2025-06-02T15:54:22Z",
  "server_info": {
    "database": "SQLite",
    "python_version": "3.11.11"
  }
}
```

### AI Chat

#### Chat with Fridge Assistant

```
POST /api/chat
Content-Type: application/json
```

Send messages to the AI assistant for recipe suggestions, food advice, etc.

**Request Body:**
```json
{
  "user_message": "What can I make with my ingredients?",
  "session_id": "optional-session-id"
}
```

**Response:**
```json
{
  "response": "Based on your items, you could make...",
  "status": "ok",
  "timestamp": "2025-06-02T16:35:12Z",
  "session_id": "session-id"
}
```

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

## Data Models

### User Item
| Field | Type | Description |
|-------|------|-------------|
| id | Integer | Unique item identifier |
| name | String | Item name |
| quantity | Integer | Item quantity |
| date_added | String | ISO 8601 timestamp |
| expiry_date | String | ISO 8601 date (optional) |

### Sensor Reading
| Field | Type | Description |
|-------|------|-------------|
| temp | Float | Temperature in Celsius |
| humidity | Float | Humidity percentage |
| gas | Float | Gas level in PPM |
| timestamp | String | ISO 8601 timestamp |

## Error Handling

All endpoints return standard HTTP status codes:
- **200**: Success
- **400**: Bad Request (invalid parameters)
- **404**: Not Found (user/item doesn't exist) 
- **500**: Internal Server Error

Error responses follow this format:
```json
{
  "status": "error",
  "message": "Error description",
  "timestamp": "2025-06-02T16:45:00Z"
}
```

## Rate Limiting

Currently no rate limiting is implemented. Future versions may include rate limiting for production use.

## Testing

Test the API using the provided test scripts:

```bash
# Test user item management
python test_local.py

# Test image upload with vision analysis
python test_with_image.py
```

## Migration Notes

When upgrading from previous versions:
1. SQLite database is automatically created
2. All upload requests now require `username` parameter
3. Previous global item data is not migrated
4. Users need to re-scan fridges to populate item lists

---

Last updated: June 2, 2025 