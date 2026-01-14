"""
Authentication Router Module

This module handles user authentication and registration for both customers and employees.

Security Features:
- Argon2 password hashing (industry standard)
- Password strength validation
- Secure password verification
"""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, EmailStr, Field
import logging
from typing import Optional

from src.crud.CRUD import execute_read, create_customer, create_employee
from src.utils.security import hash_password, verify_password, validate_password_strength
from src.model.MODEL import (
    CustomerSignupRequest, 
    EmployeeSignupRequest, 
    LoginRequest, 
    AuthResponse
)

# Initialize router and logger
router = APIRouter(prefix="/auth", tags=["auth"])
logger = logging.getLogger(__name__)


# Signup Endpoints
@router.post("/signup/customer", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def signup_customer(request: CustomerSignupRequest):
    """
    Register a new customer account.
    
    Args:
        request: CustomerSignupRequest with user details
        
    Returns:
        AuthResponse with created user information
        
    Raises:
        HTTPException: 400 if email exists or password is weak
    """
    # Validate password strength
    is_valid, error_msg = validate_password_strength(request.password)
    if not is_valid:
        raise HTTPException(status_code=400, detail=error_msg)
    
    # Check if email already exists
    existing_user = execute_read(
        "SELECT id FROM CUSTOMERS WHERE email = %s",
        (request.email,)
    )
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Hash password
    hashed_password = hash_password(request.password)
    
    # Create customer
    try:
        customer_data = {
            "name": request.name,
            "email": request.email,
            "password": hashed_password,
            "age": request.age,
            "membership": request.membership
        }
        customer = create_customer(customer_data)
        
        logger.info(f"New customer registered: {request.email}")
        
        return {
            "id": customer.id,
            "name": customer.name,
            "role": "customer",
            "email": customer.email,
            "message": "Customer account created successfully"
        }
    except Exception as e:
        logger.error(f"Error creating customer: {e}")
        raise HTTPException(status_code=500, detail="Failed to create customer account")


@router.post("/signup/employee", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def signup_employee(request: EmployeeSignupRequest):
    """
    Register a new employee account.
    
    Note: In production, this should require admin authentication.
    
    Args:
        request: EmployeeSignupRequest with employee details
        
    Returns:
        AuthResponse with created employee information
        
    Raises:
        HTTPException: 400 if email exists or password is weak
    """
    # Validate password strength
    is_valid, error_msg = validate_password_strength(request.password)
    if not is_valid:
        raise HTTPException(status_code=400, detail=error_msg)
    
    # Check if email already exists
    existing_user = execute_read(
        "SELECT id FROM EMPLOYEES WHERE email = %s",
        (request.email,)
    )
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Hash password
    hashed_password = hash_password(request.password)
    
    # Create employee
    try:
        employee_data = {
            "name": request.name,
            "email": request.email,
            "password": hashed_password,
            "age": request.age,
            "role": request.role,
            "dateOfEmployment": request.dateOfEmployment
        }
        employee = create_employee(employee_data)
        
        logger.info(f"New employee registered: {request.email}")
        
        return {
            "id": employee.id,
            "name": employee.name,
            "role": employee.role,
            "email": employee.email,
            "message": "Employee account created successfully"
        }
    except Exception as e:
        logger.error(f"Error creating employee: {e}")
        raise HTTPException(status_code=500, detail="Failed to create employee account")


# Login Endpoint
@router.post("/login", response_model=AuthResponse)
async def login(request: LoginRequest):
    """
    Authenticate a user (customer or employee) with Argon2 password verification.
    
    Args:
        request: LoginRequest containing email, password, and role
        
    Returns:
        AuthResponse with user information
        
    Raises:
        HTTPException: 401 if credentials are invalid
    """
    # Determine which table to query based on role
    table = "CUSTOMERS" if request.role == "customer" else "EMPLOYEES"
    
    # Query database for user by email only
    query = f"SELECT * FROM {table} WHERE email = %s"
    user = execute_read(query, (request.email,))
    
    # Check if user exists
    if not user:
        logger.warning(f"Login attempt for non-existent user: {request.email}")
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    # Get password from user object
    if isinstance(user, dict):
        stored_password = user.get("password")
        user_id = user["id"]
        user_name = user["name"]
        user_role = user.get("role", request.role)
        user_email = user["email"]
    else:
        user_dict = user.model_dump() if hasattr(user, 'model_dump') else dict(user)
        stored_password = user_dict.get("password")
        user_id = user_dict["id"]
        user_name = user_dict["name"]
        user_role = user_dict.get("role", request.role)
        user_email = user_dict["email"]
    
    # Verify password using Argon2
    if not stored_password:
        logger.warning(f"No password found for user: {request.email}")
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    if not verify_password(request.password, stored_password):
        logger.warning(f"Failed login attempt for {request.email}")
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    logger.info(f"Successful login for {request.email} as {request.role}")
    
    return {
        "id": user_id,
        "name": user_name,
        "role": user_role,
        "email": user_email,
        "message": "Login successful"
    }
