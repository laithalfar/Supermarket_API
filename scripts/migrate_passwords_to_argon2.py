"""
Migration Script: Convert Plain Text Passwords to Argon2 Hashes

This script migrates all existing plain text passwords in the CUSTOMERS and EMPLOYEES
tables to secure Argon2 hashes.

WARNING: This script will modify all password fields in the database.
Make sure to backup your database before running this script.
"""

import mysql.connector
import os
from dotenv import load_dotenv
from argon2 import PasswordHasher

load_dotenv()

# Database configuration
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", "0798628195Far"),
    "database": os.getenv("DB_NAME", "Supermarket"),
}

# Initialize Argon2 password hasher
ph = PasswordHasher()


def migrate_passwords():
    """Migrate all plain text passwords to Argon2 hashes."""
    conn = None
    cursor = None
    
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(dictionary=True)
        
        print("=" * 60)
        print("Password Migration to Argon2")
        print("=" * 60)
        
        # Migrate CUSTOMERS table
        print("\n1. Migrating CUSTOMERS table...")
        cursor.execute("SELECT id, email, password FROM CUSTOMERS")
        customers = cursor.fetchall()
        
        customer_count = 0
        for customer in customers:
            # Check if password is already hashed (Argon2 hashes start with $argon2)
            if customer['password'].startswith('$argon2'):
                print(f"   ⊘ Customer {customer['email']} already has hashed password")
                continue
            
            # Hash the plain text password
            hashed = ph.hash(customer['password'])
            
            # Update the database
            cursor.execute(
                "UPDATE CUSTOMERS SET password = %s WHERE id = %s",
                (hashed, customer['id'])
            )
            customer_count += 1
            print(f"   ✓ Migrated password for customer: {customer['email']}")
        
        print(f"\n   Total customers migrated: {customer_count}/{len(customers)}")
        
        # Migrate EMPLOYEES table
        print("\n2. Migrating EMPLOYEES table...")
        cursor.execute("SELECT id, email, password FROM EMPLOYEES")
        employees = cursor.fetchall()
        
        employee_count = 0
        for employee in employees:
            # Check if password is already hashed
            if employee['password'].startswith('$argon2'):
                print(f"   ⊘ Employee {employee['email']} already has hashed password")
                continue
            
            # Hash the plain text password
            hashed = ph.hash(employee['password'])
            
            # Update the database
            cursor.execute(
                "UPDATE EMPLOYEES SET password = %s WHERE id = %s",
                (hashed, employee['id'])
            )
            employee_count += 1
            print(f"   ✓ Migrated password for employee: {employee['email']}")
        
        print(f"\n   Total employees migrated: {employee_count}/{len(employees)}")
        
        # Commit changes
        conn.commit()
        
        print("\n" + "=" * 60)
        print("✓ Migration completed successfully!")
        print("=" * 60)
        print(f"\nSummary:")
        print(f"  - Customers migrated: {customer_count}")
        print(f"  - Employees migrated: {employee_count}")
        print(f"  - Total accounts migrated: {customer_count + employee_count}")
        print("\nAll passwords are now securely hashed with Argon2!")
        
    except mysql.connector.Error as err:
        print(f"\n✗ Database Error: {err}")
        if conn:
            conn.rollback()
            print("Changes rolled back.")
    except Exception as e:
        print(f"\n✗ Error: {e}")
        if conn:
            conn.rollback()
            print("Changes rolled back.")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


if __name__ == "__main__":
    print("\n⚠️  WARNING: This script will modify all passwords in the database.")
    print("Make sure you have a backup before proceeding.\n")
    
    response = input("Do you want to continue? (yes/no): ")
    
    if response.lower() in ['yes', 'y']:
        migrate_passwords()
    else:
        print("\nMigration cancelled.")
