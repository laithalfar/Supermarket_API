
import os
import sys
import unittest
from datetime import date
# Add src to path
sys.path.append(os.getcwd())

from src.crud.CRUD import (
    create_entity, execute_read, delete_entity, 
    _validate_identifier, db_transaction, execute_write
)
from src.model.MODEL import Customers, CustomerInDB
from src.utils.security import verify_password

class TestCRUDSecurity(unittest.TestCase):
    def test_password_hashing(self):
        print("\nTesting password hashing in create_entity...")
        customer_data = {
            "name": "Security Test User",
            "age": 30,
            "email": "sectest@example.com",
            "membership": True,
            "password": "PlanTextPassword123"
        }
        
        # Clean up if exists
        execute_write("DELETE FROM CUSTOMERS WHERE email = %s", ("sectest@example.com",))
        
        customer_id = create_entity("CUSTOMERS", customer_data, Customers)
        self.assertIsNotNone(customer_id)
        
        # Read back from DB
        stored = execute_read("SELECT * FROM CUSTOMERS WHERE id = %s", (customer_id,))
        self.assertIsNotNone(stored)
        
        # Verify it's hashed
        stored_password = stored["password"]
        self.assertNotEqual(stored_password, "PlanTextPassword123")
        self.assertTrue(stored_password.startswith("$argon2"))
        
        # Verify with argon2
        self.assertTrue(verify_password("PlanTextPassword123", stored_password))
        
        # Cleanup
        delete_entity("CUSTOMERS", customer_id)

    def test_identifier_validation(self):
        print("Testing identifier validation...")
        # Valid identifiers
        _validate_identifier("CUSTOMERS")
        _validate_identifier("user_name")
        
        # Invalid identifiers (SQL Injection attempts)
        with self.assertRaises(ValueError):
            _validate_identifier("CUSTOMERS; DROP TABLE USERS")
        with self.assertRaises(ValueError):
            _validate_identifier("name--")
        with self.assertRaises(ValueError):
            _validate_identifier("age=1 OR 1=1")

    def test_transaction_rollback(self):
        print("Testing transaction rollback...")
        email = "rollback@test.com"
        execute_write("DELETE FROM CUSTOMERS WHERE email = %s", (email,))
        
        try:
            with db_transaction() as conn:
                customer_data = {
                    "name": "Rollback User",
                    "age": 25,
                    "email": email,
                    "membership": False,
                    "password": "password123"
                }
                create_entity("CUSTOMERS", customer_data, Customers, connection=conn)
                
                # Verify it's created but not committed (in the same transaction)
                res = execute_read("SELECT * FROM CUSTOMERS WHERE email = %s", (email,), connection=conn)
                self.assertIsNotNone(res)
                
                # Trigger failure
                raise RuntimeError("Simulated failure")
        except RuntimeError:
            pass
            
        # Verify it was rolled back
        res = execute_read("SELECT * FROM CUSTOMERS WHERE email = %s", (email,))
        self.assertIsNone(res, "Entity should have been rolled back")

if __name__ == "__main__":
    unittest.main()
