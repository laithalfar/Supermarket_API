import requests
import json
from datetime import date, datetime

BASE_URL = "http://localhost:8000/api/v1"

def print_response(response, action):
    print(f"\n--- {action} ---")
    print(f"Status Code: {response.status_code}")
    try:
        print(f"Response Body: {json.dumps(response.json(), indent=2)}")
    except:
        print(f"Response Body: {response.text}")

def test_api():
    # 1. Test Customers
    print("\n🚀 Testing Customers...")
    customer_data = {
        "name": "Automated Test User",
        "age": 25,
        "email": f"test_{datetime.now().timestamp()}@example.com",
        "membership": True
    }
    
    # Create
    create_res = requests.post(f"{BASE_URL}/customers/", json=customer_data)
    print_response(create_res, "Create Customer")
    if create_res.status_code != 201: return
    customer_id = create_res.json()["id"]

    # Read
    read_res = requests.get(f"{BASE_URL}/customers/{customer_id}")
    print_response(read_res, "Read Customer")

    # Update
    update_data = {"name": "Updated Test User"}
    update_res = requests.put(f"{BASE_URL}/customers/{customer_id}", json=update_data)
    print_response(update_res, "Update Customer")

    # 2. Test Branches
    print("\n🚀 Testing Branches...")
    branch_data = {
        "name": "Test Branch",
        "location": "Test Location",
        "size": 100,
        "total_stock": 100
    }
    branch_res = requests.post(f"{BASE_URL}/branches/", json=branch_data)
    print_response(branch_res, "Create Branch")
    if branch_res.status_code != 201: return
    branch_id = branch_res.json()["id"]

    # 3. Test Employees
    print("\n🚀 Testing Employees...")
    employee_data = {
        "name": "Test Employee",
        "age": 30,
        "dateOfEmployment": "2023-01-01",
        "email": f"emp_{datetime.now().timestamp()}@example.com",
        "role": "CASHIER"
    }
    emp_res = requests.post(f"{BASE_URL}/employees/", json=employee_data)
    print_response(emp_res, "Create Employee")
    if emp_res.status_code != 201: return
    employee_id = emp_res.json()["id"]

    # 4. Test Products
    print("\n🚀 Testing Products...")
    product_data = {
        "name": "Test Product",
        "stock": 50,
        "sellPrice": 10.50,
        "cost": 5.00,
        "category_id": "CAT1",
        "category": "Test Category"
    }
    prod_res = requests.post(f"{BASE_URL}/products/", json=product_data)
    print_response(prod_res, "Create Product")
    if prod_res.status_code != 201: return
    product_id = prod_res.json()["id"]

    # 5. Test Transactions
    print("\n🚀 Testing Transactions...")
    transaction_data = {
        "branch_id": branch_id,
        "customer_id": customer_id,
        "employee_id": employee_id,
        "total_amount": 21.00,
        "dateOfTransaction": "2023-12-27",
        "timeOfTransaction": "12:00",
        "total": 21.00,
        "details": [
            {
                "product_id": product_id,
                "quantity": 2,
                "price": 10.50
            }
        ]
    }
    trans_res = requests.post(f"{BASE_URL}/transactions/", json=transaction_data)
    print_response(trans_res, "Create Transaction")

    # Cleanup (Optional: Delete test entities)
    print("\n🧹 Cleaning up test data...")
    requests.delete(f"{BASE_URL}/customers/{customer_id}")
    requests.delete(f"{BASE_URL}/branches/{branch_id}")
    requests.delete(f"{BASE_URL}/employees/{employee_id}")
    requests.delete(f"{BASE_URL}/products/{product_id}")
    print("Cleanup complete.")

if __name__ == "__main__":
    test_api()
