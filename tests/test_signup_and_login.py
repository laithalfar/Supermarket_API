"""
Test Script for Authentication Endpoints

Tests the new signup and login endpoints with Argon2 password hashing.
"""

import requests
import json

BASE_URL = "http://localhost:8000/api/v1"


def test_customer_signup():
    """Test customer signup endpoint."""
    print("\n" + "=" * 60)
    print("Testing Customer Signup")
    print("=" * 60)
    
    # Test 1: Valid signup
    print("\n1. Testing valid customer signup...")
    try:
        response = requests.post(
            f"{BASE_URL}/auth/signup/customer",
            json={
                "name": "Test Customer",
                "email": "testcustomer@example.com",
                "password": "SecurePass123",
                "age": 25,
                "membership": True
            }
        )
        print(f"   Status Code: {response.status_code}")
        if response.status_code == 201:
            print(f"   ✓ Success: {json.dumps(response.json(), indent=2)}")
        else:
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    # Test 2: Weak password
    print("\n2. Testing weak password (should fail)...")
    try:
        response = requests.post(
            f"{BASE_URL}/auth/signup/customer",
            json={
                "name": "Test Customer 2",
                "email": "testcustomer2@example.com",
                "password": "weak",
                "age": 25,
                "membership": False
            }
        )
        print(f"   Status Code: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    # Test 3: Duplicate email
    print("\n3. Testing duplicate email (should fail)...")
    try:
        response = requests.post(
            f"{BASE_URL}/auth/signup/customer",
            json={
                "name": "Test Customer Duplicate",
                "email": "testcustomer@example.com",
                "password": "SecurePass123",
                "age": 30,
                "membership": False
            }
        )
        print(f"   Status Code: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"   ✗ Error: {e}")


def test_employee_signup():
    """Test employee signup endpoint."""
    print("\n" + "=" * 60)
    print("Testing Employee Signup")
    print("=" * 60)
    
    print("\n1. Testing valid employee signup...")
    try:
        response = requests.post(
            f"{BASE_URL}/auth/signup/employee",
            json={
                "name": "Test Employee",
                "email": "testemployee@example.com",
                "password": "SecurePass123",
                "age": 28,
                "role": "CASHIER",
                "dateOfEmployment": "2026-01-09"
            }
        )
        print(f"   Status Code: {response.status_code}")
        if response.status_code == 201:
            print(f"   ✓ Success: {json.dumps(response.json(), indent=2)}")
        else:
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"   ✗ Error: {e}")


def test_login():
    """Test login endpoint with Argon2 verification."""
    print("\n" + "=" * 60)
    print("Testing Login with Argon2")
    print("=" * 60)
    
    # Test 1: Login with newly created customer
    print("\n1. Testing customer login...")
    try:
        response = requests.post(
            f"{BASE_URL}/auth/login",
            json={
                "email": "testcustomer@example.com",
                "password": "SecurePass123",
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
    
    # Test 2: Login with wrong password
    print("\n2. Testing wrong password (should fail)...")
    try:
        response = requests.post(
            f"{BASE_URL}/auth/login",
            json={
                "email": "testcustomer@example.com",
                "password": "WrongPassword123",
                "role": "customer"
            }
        )
        print(f"   Status Code: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    # Test 3: Login with employee
    print("\n3. Testing employee login...")
    try:
        response = requests.post(
            f"{BASE_URL}/auth/login",
            json={
                "email": "testemployee@example.com",
                "password": "SecurePass123",
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


def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("Authentication Endpoints Test Suite")
    print("=" * 60)
    
    test_customer_signup()
    test_employee_signup()
    test_login()
    
    print("\n" + "=" * 60)
    print("Test Suite Complete")
    print("=" * 60)


if __name__ == "__main__":
    main()
