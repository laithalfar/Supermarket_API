import mysql.connector

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "0798628195Far",
    "database": "Supermarket",
}

def fix_schema():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        print("Rebuilding TRANSACTION_DETAILS table...")
        
        # 1. Rename existing table
        cursor.execute("DROP TABLE IF EXISTS TRANSACTION_DETAILS_OLD")
        cursor.execute("RENAME TABLE TRANSACTION_DETAILS TO TRANSACTION_DETAILS_OLD")
        
        # 2. Create new table with correct schema
        cursor.execute("""
            CREATE TABLE TRANSACTION_DETAILS (
                id INT AUTO_INCREMENT PRIMARY KEY,
                transaction_id INT,
                product_id INT,
                quantity INT,
                price DECIMAL(10, 2),
                FOREIGN KEY (transaction_id) REFERENCES TRANSACTIONS(id),
                FOREIGN KEY (product_id) REFERENCES PRODUCTS(id)
            )
        """)
        
        # 3. Copy data back (ignoring the 'id' if we want it regenerated, or map columns)
        # Assuming old table had: transaction_id, product_id, quantity, price
        cursor.execute("""
            INSERT INTO TRANSACTION_DETAILS (transaction_id, product_id, quantity, price)
            SELECT transaction_id, product_id, quantity, price FROM TRANSACTION_DETAILS_OLD
        """)
        
        print("Data migrated. Dropping old table...")
        cursor.execute("DROP TABLE TRANSACTION_DETAILS_OLD")
        
        print("Schema fixed successfully.")
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    fix_schema()
