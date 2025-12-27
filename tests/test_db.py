# test_db.py
import os
from sqlalchemy import text
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
print(f"Connecting to database: {DATABASE_URL}")

try:
    engine = create_engine(DATABASE_URL)
    with engine.connect() as conn:
        print("Successfully connected to the database!")
        # Test query using text() to wrap the SQL
        result = conn.execute(text("SELECT 1"))
        print("Test query result:", result.scalar())
        print("✅ Database connection test successful!")
except Exception as e:
    print("Error connecting to database:", str(e))