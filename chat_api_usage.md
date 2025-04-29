# Smart Fridge Chat API Usage

This document provides instructions for using the Smart Fridge's AI chat functionality.

## Prerequisites

1. An OpenAI API key (set in `.env` file or as environment variable)
2. The Smart Fridge Simulator or hardware running
3. The API server running

## Setting Up the API Server

1. First, install the required dependencies:
   ```bash
   pip install -r simulator/requirements.txt
   ```

2. Set your OpenAI API key:
   ```bash
   # In .env file
   OPENAI_API_KEY=your_openai_api_key_here
   ```

3. Run the API server:
   ```bash
   python run_api.py
   ```

   The server will start on http://127.0.0.1:8000 by default.

## Testing the API

### Using curl

Here's a basic curl command to test the chat functionality:

```bash
curl -X POST "http://127.0.0.1:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "user_message": "What food do I have in my fridge and can I make a salad?",
    "include_image": true
  }'
```

Sample response:

```json
{
  "response": "Based on the image of your fridge, I can see some vegetables that would be perfect for a salad. I can see tomatoes and what appears to be lettuce or leafy greens. The temperature in your fridge is 3.2°C, which is within the safe range for food storage (1-5°C). Your humidity level of 45% is good for keeping produce fresh. I'd recommend making a simple salad with the fresh vegetables you have.",
  "status": "ok",
  "timestamp": "2025-04-30T15:42:23.123456"
}
```

### Using a Session ID

To maintain conversation context across multiple messages, include a session ID:

```bash
curl -X POST "http://127.0.0.1:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "user_message": "What else can I make with these ingredients?",
    "include_image": false,
    "session_id": "user123"
  }'
```

### Text-Only Mode

If you don't want to include the fridge image (faster response):

```bash
curl -X POST "http://127.0.0.1:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "user_message": "Is my fridge temperature safe for storing milk?",
    "include_image": false
  }'
```

## API Documentation

When the server is running, you can access the full API documentation at:
http://127.0.0.1:8000/docs

## Common Use Cases

1. **Food inventory questions**:
   "What food do I have in my fridge?"

2. **Recipe suggestions**:
   "What can I cook with the ingredients in my fridge?"

3. **Food safety questions**:
   "Is my fridge temperature safe for storing meat?"

4. **Freshness inquiries**:
   "How fresh are the vegetables in my fridge?"

5. **Shopping list suggestions**:
   "What should I buy based on what's missing from my fridge?"

## Troubleshooting

- **No API Key**: If you get an error about the API key, make sure your OpenAI API key is set correctly.
- **No Image Available**: If you set `include_image: true` but get a text-only response, the simulator might not have any images available.
- **Server Error**: If the server returns an error, check the logs for more details. 