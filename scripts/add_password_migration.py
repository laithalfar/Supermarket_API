import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

# Database configuration
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", "0798628195Far"),
    "database": os.getenv("DB_NAME", "Supermarket"),
}

def add_password_columns():
    """Add password columns to CUSTOMERS and EMPLOYEES tables if they don't exist."""
    conn = None
    cursor = None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Check if password column exists in CUSTOMERS table
        cursor.execute("""
            SELECT COUNT(*) 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_SCHEMA = 'Supermarket' 
            AND TABLE_NAME = 'CUSTOMERS' 
            AND COLUMN_NAME = 'password'
        """)
        customers_has_password = cursor.fetchone()[0] > 0
        
        if not customers_has_password:
            print("Adding password column to CUSTOMERS table...")
            cursor.execute("""
                ALTER TABLE CUSTOMERS 
                ADD COLUMN password VARCHAR(255) NOT NULL DEFAULT 'password123'
            """)
            print("✓ Password column added to CUSTOMERS table")
        else:
            print("✓ CUSTOMERS table already has password column")
        
        # Check if password column exists in EMPLOYEES table
        cursor.execute("""
            SELECT COUNT(*) 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_SCHEMA = 'Supermarket' 
            AND TABLE_NAME = 'EMPLOYEES' 
            AND COLUMN_NAME = 'password'
        """)
        employees_has_password = cursor.fetchone()[0] > 0
        
        if not employees_has_password:
            print("Adding password column to EMPLOYEES table...")
            cursor.execute("""
                ALTER TABLE EMPLOYEES 
                ADD COLUMN password VARCHAR(255) NOT NULL DEFAULT 'password123'
            """)
            print("✓ Password column added to EMPLOYEES table")
        else:
            print("✓ EMPLOYEES table already has password column")
        
        conn.commit()
        print("\n✓ Migration completed successfully!")
        
    except mysql.connector.Error as err:
        print(f"✗ Error: {err}")
        if conn:
            conn.rollback()
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

if __name__ == "__main__":
    add_password_columns()
