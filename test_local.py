import requests
import json

def test_local_api():
    base_url = "http://localhost:8000"
    
    print("=== Testing Local Smart Fridge API ===")
    
    # Test 1: Add an item for user 'ashish'
    print("\n1. Adding an item for user 'ashish'")
    try:
        response = requests.post(
            f"{base_url}/api/user/ashish/items",
            json={"name": "Apple", "quantity": 3}
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 2: Get items for user 'ashish'
    print("\n2. Getting items for user 'ashish'")
    try:
        response = requests.get(f"{base_url}/api/user/ashish/items")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 3: Add another item
    print("\n3. Adding another item (Banana)")
    try:
        response = requests.post(
            f"{base_url}/api/user/ashish/items",
            json={"name": "Banana", "quantity": 2}
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 4: Add same item again (should update quantity)
    print("\n4. Adding same item again (should update quantity)")
    try:
        response = requests.post(
            f"{base_url}/api/user/ashish/items",
            json={"name": "Apple", "quantity": 2}
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 5: Final items list
    print("\n5. Final items list for user 'ashish'")
    try:
        response = requests.get(f"{base_url}/api/user/ashish/items")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_local_api() 