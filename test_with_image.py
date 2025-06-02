import requests
import json
import base64
from io import BytesIO

def test_with_actual_image():
    base_url = "http://localhost:8000"
    
    print("=== Testing Image Upload with Actual Image ===")
    
    # Create a simple test image (we'll use a small PNG)
    # This is a minimal 1x1 pixel PNG in base64
    test_image_b64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChAGA60e6kgAAAABJRU5ErkJggg=="
    test_image_data = base64.b64decode(test_image_b64)
    
    print("\n1. Testing multipart upload with actual image and username 'ashish'")
    try:
        # Prepare files for multipart form
        files = {
            'data': (None, '{"user_message": "Analyze my fridge contents", "temp": 4.5, "humidity": 55.2, "gas": 120}'),
            'username': (None, 'ashish'),
            'image': ('test_fridge.png', test_image_data, 'image/png')
        }
        
        response = requests.post(f"{base_url}/api/upload/multipart", files=files)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Image processed: {result.get('image_processed')}")
            print(f"Food items detected: {result.get('food_items')}")
            print(f"Vision confidence: {result.get('vision_confidence')}")
            print(f"Guardrail result: {result.get('guardrail')}")
            if result.get('analysis'):
                print(f"Analysis: {result['analysis'][:200]}...")
        else:
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"Error: {e}")
    
    # Check user's items after upload
    print("\n2. Checking user's items after image upload")
    try:
        response = requests.get(f"{base_url}/api/user/ashish/items")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            items = response.json()
            print(f"Total items for 'ashish': {len(items)}")
            for item in items:
                print(f"  - {item['name']}: {item['quantity']}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_with_actual_image() 