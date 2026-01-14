"""
Security Utilities Module

This module provides password hashing and verification using Argon2.
Argon2 is the winner of the Password Hashing Competition and is recommended
for secure password storage.
"""

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
import logging

logger = logging.getLogger(__name__)

# Initialize Argon2 password hasher with secure defaults
ph = PasswordHasher()


def hash_password(password: str) -> str:
    """
    Hash a password using Argon2.
    
    Args:
        password: Plain text password to hash
        
    Returns:
        Hashed password string
        
    Example:
        >>> hashed = hash_password("mypassword123")
        >>> print(hashed)
        $argon2id$v=19$m=65536,t=3,p=4$...
    """
    try:
        hashed = ph.hash(password)
        logger.debug("Password hashed successfully")
        return hashed
    except Exception as e:
        logger.error(f"Error hashing password: {e}")
        raise


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against its hash using Argon2.
    
    Args:
        plain_password: Plain text password to verify
        hashed_password: Hashed password to verify against
        
    Returns:
        True if password matches, False otherwise
        
    Example:
        >>> hashed = hash_password("mypassword123")
        >>> verify_password("mypassword123", hashed)
        True
        >>> verify_password("wrongpassword", hashed)
        False
    """
    try:
        ph.verify(hashed_password, plain_password)
        
        # Check if password needs rehashing (parameters changed)
        if ph.check_needs_rehash(hashed_password):
            logger.info("Password hash needs rehashing with updated parameters")
            
        return True
    except VerifyMismatchError:
        logger.debug("Password verification failed")
        return False
    except Exception as e:
        logger.error(f"Error verifying password: {e}")
        return False


def validate_password_strength(password: str) -> tuple[bool, str]:
    """
    Validate password strength requirements.
    
    Args:
        password: Password to validate
        
    Returns:
        Tuple of (is_valid, error_message)
        
    Requirements:
        - Minimum 8 characters
        - At least one uppercase letter
        - At least one lowercase letter
        - At least one digit
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    
    if not any(c.isupper() for c in password):
        return False, "Password must contain at least one uppercase letter"
    
    if not any(c.islower() for c in password):
        return False, "Password must contain at least one lowercase letter"
    
    if not any(c.isdigit() for c in password):
        return False, "Password must contain at least one digit"
    
    return True, ""
