'''
 Create a database connection using SQLAlchemy, because i want to use sqlalchemy to connect 
 to the database and create a session. This way we can use sqlalchemy to create a database 
 and tables, and also to insert, update, delete, and query data from the database without using pure SQL.
'''

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase, Session
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not set in environment variables. Please check your .env file.")

# Create SQLAlchemy engine
engine = create_engine(DATABASE_URL, pool_pre_ping=True)

# SessionLocal class for dependency injection
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models to inherit from (SQLAlchemy 2.0 style)
class Base(DeclarativeBase):
    pass

# function to get DB session
def get_db():
    """Dependency to get DB session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
