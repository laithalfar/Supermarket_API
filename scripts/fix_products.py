import os
import mysql.connector

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "0798628195Far",
    "database": "Supermarket",
}

def check_products():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM PRODUCTS")
        products = cursor.fetchall()
        print(f"Found {len(products)} products.")
        
        invalid_count = 0
        for p in products:
            if p['sellPrice'] < 0 or p['cost'] < 0 or p['stock'] < 0:
                print(f"INVALID PRODUCT FOUND: ID={p['id']}, Name={p['name']}, Price={p['sellPrice']}, Stock={p['stock']}")
                invalid_count += 1
                # Fix: set negative prices/stock to 0
                new_price = max(0, p['sellPrice'])
                new_cost = max(0, p['cost'])
                new_stock = max(0, p['stock'])
                cursor.execute("UPDATE PRODUCTS SET sellPrice=%s, cost=%s, stock=%s WHERE id=%s", (new_price, new_cost, new_stock, p['id']))
        
        if invalid_count > 0:
            conn.commit()
            print(f"Fixed {invalid_count} invalid products.")
        else:
            print("No invalid products found.")
            
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_products()
