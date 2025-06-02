"""
Simple script to test the Smart Fridge backend API.
"""
import requests
import json
import base64
import os
from datetime import datetime

# Backend API URL
API_URL = "https://smart-fridge-backend.onrender.com/api"

def load_test_image():
    """Load a test image from the simulator directory"""
    # Find the most recent image in the simulator/mock_images directory
    image_dir = "simulator/mock_images"
    if not os.path.exists(image_dir):
        print(f"Error: Directory {image_dir} not found")
        return None
        
    image_files = [f for f in os.listdir(image_dir) if f.endswith('.jpg')]
    if not image_files:
        print(f"Error: No images found in {image_dir}")
        return None
        
    # Get the most recent image
    latest_image = sorted(image_files)[-1]
    image_path = os.path.join(image_dir, latest_image)
    
    print(f"Using test image: {image_path}")
    
    # Read and encode the image
    with open(image_path, "rb") as f:
        image_data = f.read()
        image_base64 = base64.b64encode(image_data).decode('utf-8')
    
    return image_base64

def test_upload_endpoint():
    """Test the upload endpoint with mock data"""
    image_base64 = load_test_image()
    if not image_base64:
        print("Failed to load test image")
        return
    
    # Prepare test data
    test_data = {
        "temp": 4.2,
        "humidity": 55.0,
        "gas": 120,
        "image_base64": image_base64,
        "debug": True  # Add debug flag to see more details
    }
    
    print(f"Sending test data to {API_URL}/upload")
    print(f"Data: temp={test_data['temp']}°C, humidity={test_data['humidity']}%, gas={test_data['gas']} PPM")
    
    try:
        # Send request to upload endpoint
        response = requests.post(
            f"{API_URL}/upload",
            json=test_data,
            headers={"Content-Type": "application/json"},
            timeout=60  # Longer timeout as analysis can take time
        )
        
        # Check response
        if response.status_code == 200:
            print("Upload successful!")
            
            # Parse and display response
            result = response.json()
            print("\nResponse:")
            print(f"Status: {result.get('status')}")
            print(f"Temperature: {result.get('temp')}°C")
            print(f"Humidity: {result.get('humidity')}%")
            print(f"Gas Level: {result.get('gas')} PPM")
            print(f"Detected Items: {', '.join(result.get('items', []))}")
            print(f"AI Response: {result.get('ai_response')}")
            
            # Save the full response to file for inspection
            with open("api_response.json", "w") as f:
                json.dump(result, f, indent=2)
            print("\nFull response saved to api_response.json")
            
        else:
            print(f"Upload failed: HTTP {response.status_code}")
            print(f"Response: {response.text}")
    
    except Exception as e:
        print(f"Error: {str(e)}")

def test_status_endpoint():
    """Test the fridge-status endpoint"""
    print(f"Checking fridge status at {API_URL}/fridge-status")
    
    try:
        # Send request to status endpoint
        response = requests.get(
            f"{API_URL}/fridge-status",
            timeout=10
        )
        
        # Check response
        if response.status_code == 200:
            print("Status check successful!")
            
            # Parse and display response summary
            result = response.json()
            print("\nLatest Fridge Status:")
            print(f"Temperature: {result.get('temp')}°C")
            print(f"Humidity: {result.get('humidity')}%")
            print(f"Gas Level: {result.get('gas')} PPM")
            print(f"Items: {', '.join(result.get('items', []))}")
            
            # Save the full response to file for inspection
            with open("status_response.json", "w") as f:
                json.dump(result, f, indent=2)
            print("\nFull status saved to status_response.json")
            
        else:
            print(f"Status check failed: HTTP {response.status_code}")
            print(f"Response: {response.text}")
    
    except Exception as e:
        print(f"Error: {str(e)}")

def test_notifications_endpoint():
    """Test the notifications endpoint"""
    print(f"Checking notifications at {API_URL}/notifications")
    
    try:
        # Send request to notifications endpoint
        response = requests.get(
            f"{API_URL}/notifications",
            timeout=10
        )
        
        # Check response
        if response.status_code == 200:
            print("Notifications check successful!")
            
            # Parse and display response
            result = response.json()
            print(f"\nUnread notifications: {result.get('unread_count', 0)}")
            
            notifications = result.get('notifications', [])
            print(f"Total notifications: {len(notifications)}")
            
            # Show the most recent notifications
            if notifications:
                print("\nLatest notifications:")
                for i, notification in enumerate(notifications[:3]):  # Show top 3
                    print(f"{i+1}. {notification.get('title')} ({notification.get('type')})")
                    print(f"   {notification.get('message')[:100]}...")
            
            # Save the full response to file for inspection
            with open("notifications_response.json", "w") as f:
                json.dump(result, f, indent=2)
            print("\nFull notifications saved to notifications_response.json")
            
        else:
            print(f"Notifications check failed: HTTP {response.status_code}")
            print(f"Response: {response.text}")
    
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    print("=== Smart Fridge API Test ===")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"API URL: {API_URL}")
    print("===========================\n")
    
    # Test all endpoints
    test_status_endpoint()
    print("\n" + "-"*30 + "\n")
    test_notifications_endpoint()
    print("\n" + "-"*30 + "\n")
    test_upload_endpoint()  # This may take longer due to AI processing

    # Test 1: Add an item for user 'ashish'
    print("=== Test 1: Adding an item for user 'ashish' ===")
    response = requests.post(
        "http://localhost:8000/api/user/ashish/items",
        json={"name": "Apple", "quantity": 3}
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()

    # Test 2: Get items for user 'ashish'
    print("=== Test 2: Getting items for user 'ashish' ===")
    response = requests.get("http://localhost:8000/api/user/ashish/items")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()

    # Test 3: Add another item for user 'ashish'
    print("=== Test 3: Adding another item for user 'ashish' ===")
    response = requests.post(
        "http://localhost:8000/api/user/ashish/items",
        json={"name": "Banana", "quantity": 2}
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()

    # Test 4: Add the same item again (should update quantity)
    print("=== Test 4: Adding same item again (should update quantity) ===")
    response = requests.post(
        "http://localhost:8000/api/user/ashish/items",
        json={"name": "Apple", "quantity": 2}
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()

    # Test 5: Get final items list
    print("=== Test 5: Final items list for user 'ashish' ===")
    response = requests.get("http://localhost:8000/api/user/ashish/items")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()

    # Test 6: Test image upload with form data
    print("=== Test 6: Test multipart upload with username ===")
    files = {
        'data': (None, '{"user_message": "Analyze my fridge"}'),
        'username': (None, 'ashish')
    }
    response = requests.post("http://localhost:8000/api/upload/multipart", files=files)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print(f"Response: {response.json()}")
    else:
        print(f"Error: {response.text}") 