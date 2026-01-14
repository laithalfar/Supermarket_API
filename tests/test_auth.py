import requests
import json

# Test the login endpoint
BASE_URL = "http://localhost:8000"

def test_login():
    """Test the login endpoint with different scenarios."""
    
    print("=" * 60)
    print("Testing Authentication Endpoint")
    print("=" * 60)
    
    # Test 1: Try to login as a customer
    print("\n1. Testing customer login...")
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/auth/login",
            json={
                "email": "john@example.com",
                "password": "password123",
                "role": "customer"
            }
        )
        print(f"   Status Code: {response.status_code}")
        if response.status_code == 200:
            print(f"   ✓ Success: {json.dumps(response.json(), indent=2)}")
        else:
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    # Test 2: Try to login as an employee
    print("\n2. Testing employee login...")
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/auth/login",
            json={
                "email": "employee@example.com",
                "password": "password123",
                "role": "admin"
            }
        )
        print(f"   Status Code: {response.status_code}")
        if response.status_code == 200:
            print(f"   ✓ Success: {json.dumps(response.json(), indent=2)}")
        else:
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    # Test 3: Try with invalid credentials
    print("\n3. Testing invalid credentials...")
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/auth/login",
            json={
                "email": "invalid@example.com",
                "password": "wrongpassword",
                "role": "customer"
            }
        )
        print(f"   Status Code: {response.status_code}")
        print(f"   Response: {response.text}")
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    test_login()
