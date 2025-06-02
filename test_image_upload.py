import requests
import json

def test_image_upload():
    base_url = "http://localhost:8000"
    
    print("=== Testing Image Upload with Username ===")
    
    # Test the multipart upload endpoint
    print("\n1. Testing multipart upload with username 'ashish'")
    try:
        # Prepare form data
        files = {
            'data': (None, '{"user_message": "Analyze my fridge contents"}'),
            'username': (None, 'ashish')
        }
        
        response = requests.post(f"{base_url}/api/upload/multipart", files=files)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Response: {json.dumps(result, indent=2)}")
        else:
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"Error: {e}")
    
    # Check user's items after upload
    print("\n2. Checking user's items after upload")
    try:
        response = requests.get(f"{base_url}/api/user/ashish/items")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            items = response.json()
            print(f"Current items for 'ashish': {json.dumps(items, indent=2)}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_image_upload() 