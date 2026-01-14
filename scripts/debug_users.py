import mysql.connector
import json

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "0798628195Far",
    "database": "Supermarket",
}

def check_users():
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("SELECT id, name, email, password FROM CUSTOMERS")
    customers = cursor.fetchall()
        
    cursor.execute("SELECT id, name, email, password FROM EMPLOYEES")
    employees = cursor.fetchall()
    
    with open("users_output.json", "w", encoding="utf-8") as f:
        json.dump({"customers": customers, "employees": employees}, f, indent=2, default=str)
        
    conn.close()

if __name__ == "__main__":
    check_users()
