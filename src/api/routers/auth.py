from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel, EmailStr, Field
import logging
from typing import Optional
from datetime import timedelta

from sqlalchemy.orm import Session
from src.database import get_db
from src.crud import CRUD
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
async def signup_customer(request: CustomerSignupRequest, db: Session = Depends(get_db)):
    """Register a new customer account."""

    # 1. Validate password strength
    is_valid, error_msg = validate_password_strength(request.password)
    if not is_valid:
        raise HTTPException(status_code=400, detail=error_msg)
    
    # 2. Cross-table email uniqueness check
    # Check if email exists in CUSTOMERS
    if CRUD.get_customers(db, email=request.email):
        raise HTTPException(status_code=400, detail="Email already registered as a customer")
    
    # Check if email exists in EMPLOYEES
    if CRUD.get_employees(db, email=request.email):
        raise HTTPException(status_code=400, detail="Email already registered as staff")
    
    # 3. Create customer record
    # Note: CRUD.create_customer handles hashing the password
    try:
        customer_data = {
            "name": request.name,
            "email": request.email,
            "password": request.password, # Pass plain password, CRUD handles hashing
            "age": request.age,
            "membership": request.membership
        }

        customer = CRUD.create_customer(db, customer_data)
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
        # Return clearer message if it's likely a data issue
        detail = str(e) if "integrity" in str(e).lower() else "Failed to create customer account"
        raise HTTPException(status_code=400, detail=detail)


# Employee endpoint on the signup
@router.post("/signup/employee", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def signup_employee(request: EmployeeSignupRequest, db: Session = Depends(get_db)):
    """Register a new employee account."""

    # 1. Validate password strength
    is_valid, error_msg = validate_password_strength(request.password)
    if not is_valid:
        raise HTTPException(status_code=400, detail=error_msg)
    
    # 2. Cross-table email uniqueness check
    if CRUD.get_customers(db, email=request.email):
        raise HTTPException(status_code=400, detail="Email already registered as a customer")
    
    if CRUD.get_employees(db, email=request.email):
        raise HTTPException(status_code=400, detail="Email already registered as staff")
    
    # 3. Create employee record
    # Note: CRUD.create_employee handles hashing the password
    try:
        employee_data = {
            "name": request.name,
            "email": request.email,
            "password": request.password,
            "age": request.age,
            "role": request.role,
            "dateOfEmployment": request.dateOfEmployment # Already a date object from Pydantic
        }

        employee = CRUD.create_employee(db, employee_data)
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
        detail = str(e) if "integrity" in str(e).lower() else "Failed to create employee account"
        raise HTTPException(status_code=400, detail=detail)


# Login Endpoint
@router.post("/login", response_model=AuthResponse)
async def login(request: LoginRequest, db: Session = Depends(get_db)):
    """Authenticate a user and return a JWT access token."""

    # Determine table based on role
    table = "CUSTOMERS" if request.role == "customer" else "EMPLOYEES"

    # Fetch user by email
    if request.role == "customer":
        users = CRUD.get_customers(db, email=request.email)
    else:
        users = CRUD.get_employees(db, email=request.email)
    
    user = users[0] if users else None
    
    # Check if user exists
    if not user:
        logger.warning(f"Login attempt for non-existent user: {request.email}")
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    # Access user attributes directly from ORM object
    stored_password = user.password
    user_id = user.id
    user_name = user.name
    user_role = getattr(user, "role", request.role)
    user_email = user.email
    
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
