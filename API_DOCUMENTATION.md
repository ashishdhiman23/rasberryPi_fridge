# Smart Fridge API Documentation

## Overview

This document provides comprehensive API documentation for the Smart Fridge system. The API allows mobile applications, web dashboards, and other clients to interact with the Smart Fridge backend, access sensor data, detect food items, and chat with the AI assistant.

**Production Base URL**: `https://smart-fridge-backend.onrender.com/api`

## System Architecture

The Smart Fridge system consists of the following components:

1. **Raspberry Pi Hardware**: Physical implementation with real sensors and camera
2. **Simulator**: Software that mimics the Raspberry Pi's functionality for testing
3. **Backend API**: FastAPI service that processes data and provides endpoints
4. **Frontend Dashboard**: Web interface for visualization and interaction
5. **Mobile App**: Native mobile application (future development)

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
  "timestamp": "2025-04-29T15:54:22.182387",
  "server_info": {
    "render_instance": "srv-d07il6qli9vc73fb2obg-hibernate-6d47bfc7f4-ns8m2",
    "python_version": "3.11.11"
  }
}
```

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
  "timestamp": "2025-04-29T16:30:45.123456"
}
```

#### Upload Sensor Data and Images

Upload sensor readings and fridge images. This endpoint uses `multipart/form-data` format to handle both JSON data and image files.

**Endpoint**: `POST /upload/multipart`

**Request Parameters**:
- `data` (form field): JSON string containing sensor readings
  ```json
  {
    "temp": 4.2,
    "humidity": 52.3,
    "gas": 125,
    "timestamp": "2025-04-29T16:40:00.000000"
  }
  ```
- `image` (file, optional): Image file of fridge contents (JPEG or PNG)

**Response**:
```json
{
  "status": "success",
  "message": "Data received and processed",
  "timestamp": "2025-04-29T16:40:05.789012",
  "image_processed": true,
  "food_items": ["milk", "eggs"],
  "temperature_status": "normal"
}
```

### AI Assistant Endpoints

#### Chat with Fridge

Send messages to the AI assistant to ask questions about fridge contents, get recipe suggestions, or inquire about food safety.

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
  "response": "With milk, eggs, cheese, and yogurt, you could make a quiche, an omelet, or a yogurt parfait. The leftovers might also be incorporated depending on what they are.",
  "status": "ok",
  "timestamp": "2025-04-29T16:35:12.654321",
  "session_id": "generated-or-provided-session-id"
}
```

## Data Models

### Sensor Data

| Field | Type | Description |
|-------|------|-------------|
| temp | float | Temperature in Celsius |
| humidity | float | Humidity percentage |
| gas | float | Gas level in PPM |
| timestamp | string | ISO 8601 timestamp |

### Food Item

Each food item is represented as a string in the array. Future versions may use objects with additional metadata:

```json
{
  "name": "milk",
  "detected_at": "2025-04-25T10:30:00.000000",
  "expires_at": "2025-05-01T23:59:59.000000",
  "location": "door"
}
```

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
  "message": "Error processing upload: Invalid data format",
  "timestamp": "2025-04-29T16:45:00.000000"
}
```

## Implementation Examples

### Mobile App Integration

Here are examples of how to integrate with the Smart Fridge API in various programming languages:

#### Android (Kotlin)

```kotlin
// Example: Fetching fridge status
private fun fetchFridgeStatus() {
    val url = "https://smart-fridge-backend.onrender.com/api/fridge-status"
    
    val request = Request.Builder()
        .url(url)
        .build()
        
    OkHttpClient().newCall(request).enqueue(object : Callback {
        override fun onFailure(call: Call, e: IOException) {
            // Handle error
        }
        
        override fun onResponse(call: Call, response: Response) {
            if (response.isSuccessful) {
                val responseData = response.body?.string()
                val fridgeData = JSONObject(responseData)
                
                // Process data
                val temperature = fridgeData.getDouble("temp")
                val items = fridgeData.getJSONArray("items")
                
                // Update UI with data
                runOnUiThread {
                    updateDashboard(temperature, items)
                }
            }
        }
    })
}
```

#### iOS (Swift)

```swift
// Example: Sending a chat message
func sendChatMessage(message: String, completion: @escaping (Result<ChatResponse, Error>) -> Void) {
    let url = URL(string: "https://smart-fridge-backend.onrender.com/api/chat")!
    var request = URLRequest(url: url)
    request.httpMethod = "POST"
    request.addValue("application/json", forHTTPHeaderField: "Content-Type")
    
    let sessionId = UserDefaults.standard.string(forKey: "chatSessionId") ?? UUID().uuidString
    
    let body: [String: Any] = [
        "user_message": message,
        "session_id": sessionId
    ]
    
    request.httpBody = try? JSONSerialization.data(withJSONObject: body)
    
    URLSession.shared.dataTask(with: request) { data, response, error in
        if let error = error {
            completion(.failure(error))
            return
        }
        
        guard let data = data else {
            completion(.failure(NSError(domain: "No data", code: 0)))
            return
        }
        
        do {
            let decoder = JSONDecoder()
            let response = try decoder.decode(ChatResponse.self, from: data)
            
            // Save session ID for future messages
            UserDefaults.standard.set(response.session_id, forKey: "chatSessionId")
            
            completion(.success(response))
        } catch {
            completion(.failure(error))
        }
    }.resume()
}
```

### React Native Example

```javascript
// Example: Uploading sensor data with image
const uploadData = async (sensorData, imageUri) => {
  try {
    const formData = new FormData();
    
    // Add sensor data as JSON string
    formData.append('data', JSON.stringify({
      temp: sensorData.temperature,
      humidity: sensorData.humidity,
      gas: sensorData.gasLevel,
      timestamp: new Date().toISOString()
    }));
    
    // Add image if available
    if (imageUri) {
      formData.append('image', {
        uri: imageUri,
        type: 'image/jpeg',
        name: 'fridge_image.jpg'
      });
    }
    
    const response = await fetch(
      'https://smart-fridge-backend.onrender.com/api/upload/multipart',
      {
        method: 'POST',
        body: formData,
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      }
    );
    
    const result = await response.json();
    
    if (result.status === 'success') {
      console.log('Upload successful:', result);
      return true;
    } else {
      console.error('Upload failed:', result);
      return false;
    }
  } catch (error) {
    console.error('Error uploading data:', error);
    return false;
  }
};
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

Last updated: April 29, 2025 