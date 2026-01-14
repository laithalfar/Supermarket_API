import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

def test_oauth2():
    print("Testing OAuth2 implementation...")
    
    # 1. Try to access a protected route without a token
    print("\n1. Accessing /products without token:")
    try:
        resp = requests.get(f"{BASE_URL}/products")
        print(f"   Status: {resp.status_code}")
        if resp.status_code == 401:
            print("   ✓ Correctly denied access (401)")
        else:
            print(f"   ✗ Unexpected status code: {resp.status_code}")
    except requests.exceptions.ConnectionError:
        print("   ✗ Could not connect to server. Startup server first.")
        return

    # 2. Login to get a token
    print("\n2. Attempting login:")
    login_data = {
        "email": "test@example.com",
        "password": "Password123!", # Updated to match strength requirements
        "role": "customer"
    }
    
    # Signup if doesn't exist (optional step for test reliability)
    signup_data = {
        "name": "Test User",
        "email": "test@example.com",
        "password": "Password123!",
        "age": 30,
        "membership": True
    }
    requests.post(f"{BASE_URL}/auth/signup/customer", json=signup_data)
    
    resp = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    print(f"   Login Status: {resp.status_code}")
    
    if resp.status_code == 200:
        token = resp.json().get("access_token")
        print("   ✓ Login successful, token received")
        
        # 3. Access protected route with token
        print("\n3. Accessing /products with token:")
        headers = {"Authorization": f"Bearer {token}"}
        resp = requests.get(f"{BASE_URL}/products", headers=headers)
        print(f"   Status: {resp.status_code}")
        if resp.status_code == 200:
            print("   ✓ Access granted (200)")
        else:
            print(f"   ✗ Failed to access protected route: {resp.text}")
            
        # 4. Check /me endpoint
        print("\n4. Checking /auth/me:")
        resp = requests.get(f"{BASE_URL}/auth/me", headers=headers)
        print(f"   Status: {resp.status_code}")
        if resp.status_code == 200:
            print(f"   ✓ User identity verified: {resp.json().get('email')}")
        else:
            print(f"   ✗ Failed to verify identity")
    else:
        print(f"   ✗ Login failed: {resp.text}")

if __name__ == "__main__":
    test_oauth2()
