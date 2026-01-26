'''
Docstring for src.utils.security
Utility functions for password hashing, JWT token creation, and user authentication.

'''

import os
import logging
from datetime import datetime, timedelta
from typing import Optional, Any, Dict, Union
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

from src.crud.CRUD import execute_read
from src.model.MODEL import TokenData

# Security Configuration
# Get secret key from environment variable
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY is not set in environment variables. Please check your .env file.")

#Get algorithm from environment variable
ALGORITHM = os.getenv("ALGORITHM")
if not ALGORITHM:
    raise RuntimeError("ALGORITHM is not set in environment variables.")

#Get expire minutes from environment variable
expire_minutes_str = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")
if not expire_minutes_str:
    raise RuntimeError("ACCESS_TOKEN_EXPIRE_MINUTES is not set in environment variables.")

#Convert expire minutes to integer
try:
    ACCESS_TOKEN_EXPIRE_MINUTES = int(expire_minutes_str)
except ValueError:
    raise RuntimeError("ACCESS_TOKEN_EXPIRE_MINUTES must be an integer.")

# Get OAuth2 scheme for token extraction
# The tokenUrl should point to the login endpoint
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")

logger = logging.getLogger(__name__)

# Initialize Argon2 password hasher with secure defaults
ph = PasswordHasher()


# Password Hashing with argon2
def hash_password(password: str) -> str:
    """Hash a password using Argon2."""
    try:
        hashed = ph.hash(password)
        logger.debug("Password hashed successfully")
        return hashed
    except Exception as e:
        logger.error(f"Error hashing password: {e}")
        raise

# Verify entered password against the stored hash
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash using Argon2."""
    try:
        ph.verify(hashed_password, plain_password)
        if ph.check_needs_rehash(hashed_password):
            logger.info("Password hash needs rehashing with updated parameters")
        return True
    except VerifyMismatchError:
        logger.debug("Password verification failed")
        return False
    except Exception as e:
        logger.error(f"Error verifying password: {e}")
        return False


# Validate password strength before allowing it to be set
def validate_password_strength(password: str) -> tuple[bool, str]:
    """Validate password strength requirements."""
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    if not any(c.isupper() for c in password):
        return False, "Password must contain at least one uppercase letter"
    if not any(c.islower() for c in password):
        return False, "Password must contain at least one lowercase letter"
    if not any(c.isdigit() for c in password):
        return False, "Password must contain at least one digit"
    return True, ""

## data is dictionary
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create a new JWT access token."""
    to_encode = data.copy()
    # if an expiry time is set then use it else use default expiry time of 15 minutes
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    
    # add expiry time to data
    to_encode.update({"exp": expire})
    
    # encode data
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# get the current active user
async def get_current_user(token: str = Depends(oauth2_scheme)):
    """Dependency to validate JWT and return current user identifier."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # decode token
    try:
        logger.info(f"Attempting to decode token (first 10 chars): {token[:10]}...")
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        role: str = payload.get("role")
        logger.info(f"Token decoded successfully for user: {email}")

        #validate decoded email and role
        if email is None:
            logger.warning("Token decoded but 'sub' (email) is missing")
            raise credentials_exception
        token_data = TokenData(email=email, role=role)
    except JWTError as e:
        logger.warning(f"JWT decoding failed: {str(e)}")
        raise credentials_exception
    except Exception as e:
        logger.error(f"Unexpected error during token validation: {str(e)}")
        raise credentials_exception
    
    # Optional: Verify user exists in database
    # For now, we trust the token payload for efficiency, 
    # but a full check would be:
    # user = execute_read("SELECT id FROM CUSTOMERS WHERE email = %s UNION SELECT id FROM EMPLOYEES WHERE email = %s", (token_data.email, token_data.email))
    # if user is None:
    #     raise credentials_exception
    
    #return decoded email and role
    return token_data
