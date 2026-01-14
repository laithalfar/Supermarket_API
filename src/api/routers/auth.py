from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel, EmailStr, Field
import logging
from typing import Optional
from datetime import timedelta

from src.crud.CRUD import execute_read, create_customer, create_employee
from src.utils.security import (
    hash_password, 
    verify_password, 
    validate_password_strength,
    create_access_token,
    get_current_user,
    ACCESS_TOKEN_EXPIRE_MINUTES
)

from src.model.MODEL import (
    CustomerSignupRequest, 
    EmployeeSignupRequest, 
    LoginRequest, 
    AuthResponse,
    TokenData
)

# Initialize router for auth page and logger
router = APIRouter(prefix="/auth", tags=["auth"])
logger = logging.getLogger(__name__)


# Signup Endpoints 
# customer endpoint on the signup
@router.post("/signup/customer", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def signup_customer(request: CustomerSignupRequest):
    """Register a new customer account."""

    # validate password strength
    is_valid, error_msg = validate_password_strength(request.password)
    if not is_valid:
        raise HTTPException(status_code=400, detail=error_msg)
    
    # Check if email already exists
    existing_user = execute_read(
        "SELECT id FROM CUSTOMERS WHERE email = %s",
        (request.email,)
    )

    # If email exists, raise error
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Hash the password
    hashed_password = hash_password(request.password)
    
    # Create customer record using hashed password
    try:
        customer_data = {
            "name": request.name,
            "email": request.email,
            "password": hashed_password,
            "age": request.age,
            "membership": request.membership
        }

        # Create customer in the database using dict
        customer = create_customer(customer_data)
        logger.info(f"New customer registered: {request.email}")
        
        # Return success response
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


# Employee endpoint on the signup
@router.post("/signup/employee", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def signup_employee(request: EmployeeSignupRequest):
    """Register a new employee account."""

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
    
    # Hash the password
    hashed_password = hash_password(request.password)
    
    # Create employee record using hashed password
    try:
        employee_data = {
            "name": request.name,
            "email": request.email,
            "password": hashed_password,
            "age": request.age,
            "role": request.role,
            "dateOfEmployment": request.dateOfEmployment
        }

        # Create employee in the database using dict
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
    """Authenticate a user and return a JWT access token."""

    # Determine table based on role
    table = "CUSTOMERS" if request.role == "customer" else "EMPLOYEES"

    # Fetch user by email
    query = f"SELECT * FROM {table} WHERE email = %s"
    user = execute_read(query, (request.email,))
    
    # Check if user exists
    if not user:
        logger.warning(f"Login attempt for non-existent user: {request.email}")
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    # Handle both dict and model results
    if isinstance(user, dict):
        stored_password = user.get("password")
        user_id = user["id"]
        user_name = user["name"]
        user_role = user.get("role", request.role)
        user_email = user["email"]
    else:
        # Change model to dict
        user_dict = user.model_dump() if hasattr(user, 'model_dump') else dict(user)
        stored_password = user_dict.get("password")
        user_id = user_dict["id"]
        user_name = user_dict["name"]
        user_role = user_dict.get("role", request.role)
        user_email = user_dict["email"]
    
    # Verify password
    if not stored_password or not verify_password(request.password, stored_password):
        logger.warning(f"Failed login attempt for {request.email}")
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    # Generate timedelta for token expiry
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    # Create JWT access token
    access_token = create_access_token(
        data={"sub": user_email, "role": user_role},
        expires_delta=access_token_expires
    )
    
    logger.info(f"Successful login and token generation for {request.email}")
    
    return {
        "id": user_id,
        "name": user_name,
        "role": user_role,
        "email": user_email,
        "message": "Login successful",
        "access_token": access_token,
        "token_type": "bearer"
    }

# Get Current User Endpoint
@router.get("/me", response_model=TokenData)
async def get_me(current_user: TokenData = Depends(get_current_user)):
    """Return currently authenticated user information."""
    return current_user
