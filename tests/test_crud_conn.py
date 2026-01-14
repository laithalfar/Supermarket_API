
import os
import sys
# Add src to path
sys.path.append(os.getcwd())

from src.crud.CRUD import get_connection_pool, get_cursor

def test_crud_connection():
    print("Testing CRUD.py connection...")
    try:
        pool = get_connection_pool()
        print(f"Pool initialized: {pool.pool_name}")
        with get_cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            print(f"Query result: {result}")
        print("✅ CRUD.py connection successful!")
    except Exception as e:
        print(f"❌ CRUD.py connection failed: {e}")
        # Print environment to debug
        print(f"DB_HOST: {os.getenv('DB_HOST')}")
        print(f"DB_USER: {os.getenv('DB_USER')}")
        print(f"DB_PASSWORD is set: {bool(os.getenv('DB_PASSWORD'))}")
        print(f"DB_NAME: {os.getenv('DB_NAME')}")

if __name__ == "__main__":
    test_crud_connection()
