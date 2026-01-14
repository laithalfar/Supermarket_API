import requests
import json

base_url = "http://localhost:8000/api/v1/auth"

def test_signup():
    payload = {
        "name": "Employee User",
        "email": "employee_fix_2026@example.com",
        "password": "Password123",
        "age": 35,
        "role": "CASHIER",
        "dateOfEmployment": "2026-01-10"
    }
    
    print(f"Testing signup with payload: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(f"{base_url}/signup/employee", json=payload)
        print(f"Status Code: {response.status_code}")
        print(f"Response Body: {response.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_signup()
