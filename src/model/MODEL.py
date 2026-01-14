''' 
- MODEL file with initialization of all BASE models. 

- Each model is initialized with validation using pydantic.

- Create and Update Functions are applied using BASE Model of the tables.

- Database models are made to read from the database.

- These functions and models are for sqlalchemy to communicate with the database once a response is sent from the HTTP.

'''

from datetime import date, time, datetime
from decimal import Decimal
from enum import Enum
from typing import Optional, List, ClassVar, Any
import enum
from dataclasses import dataclass
from pydantic import (
    BaseModel,
    EmailStr, # applies validation for a variable to have the basics of an email address
    Field, # applies validation to a variable
    conint,
    condecimal,
    constr,
    ValidationError
)

class Role(enum.StrEnum):
    ADMIN = "ADMIN"
    MANAGER = "MANAGER"
    HEAD_OF_BRANCH = "HEAD_OF_BRANCH"
    STOCKER = "STOCKER"
    CASHIER = "CASHIER"


class Customers(BaseModel):
    name: constr(min_length=1, max_length=100) = Field(examples=["John Doe", "Jane Doe"], description = "name of customer")
    age: conint(gt=0, lt=120) = Field(examples=["7", "8"], description = "age of customer")
    email: EmailStr = Field(examples=["example@gmd.jo"], description = "email address of customer")
    membership: bool = Field(examples=[True, False], description = "customer membership status")
    password: constr(min_length=6) = Field(default="password123", description="password for customer login")

def validate_customer(data: dict):
    try:
        customer = Customers.model_validate(data)
        print(customer)
    except ValidationError as e:
        print("Customer invalid")
        for error in e.errors():
            print(error)

class Employees(BaseModel):
    name: constr(min_length=1, max_length=100) = Field(examples=["John Doe", "Jane Doe"], description = "name of employee")
    age: conint(gt=17, lt=120) = Field(examples=["18", "25"], description = "age of employee")
    dateOfEmployment: date = Field(examples=["2023-01-01", "2023-01-02"], description = "date of employment of employee")
    dateOfEndOfEmployment: Optional[date] = Field(default=None, examples=["2023-01-01", "2023-01-02"], description = "date of the end of employment of an employee which can be empty if employee is stll working")
    email: EmailStr = Field(examples=["example@gmd.jo"], description = "email address of customer", frozen = True)
    role: Role = Field(examples=["HEADOFBRANCH", "CASHIER"], description = "role of employee")
    password: constr(min_length=6) = Field(default="password123", description="password for employee login")

def validate_employee(data: dict):
    try:
        employee = Employees.model_validate(data)
        print(employee)
    except ValidationError as e:
        print("Customer invalid")
        for error in e.errors():
            print(error)


class Products(BaseModel):
    name: constr(min_length=1, max_length=100) = Field(examples=["Chicken sandwich", "redbull drink"], description = "Uname of product")
    stock: conint(ge=0) = Field(examples=["30", "1523"], description = "amount of stock for this product")
    sellPrice: condecimal(ge=0) = Field(examples=["30.02", "97.00"], description = "selling price of product in Jordanian Dinar for customers")
    cost: condecimal(ge=0) = Field(examples=["11.20", "40.57"], description = "buying price of product in Jordanian Dinar for supermarket")
    category_id: constr(max_length=10) = Field(examples=["1", "2"], description = "Unique id of the category of the product") # Main category (e.g., 1 = Food, 2 = Drinks, etc.)
    category: constr(min_length=1, max_length=50) = Field(examples=["healthy Food", "energy Drinks"], description = "name of the category of the product") # Subcategory (e.g., "Meat", "Chicken", "Vegetables")

def validate_product(data: dict):
    try:
        product = Products.model_validate(data)
        print(product)
    except ValidationError as e:
        print("product invalid")
        for error in e.errors():
            print(error)


class Branches(BaseModel):
    name: constr(min_length=1, max_length=100) = Field(examples=["Main Branch", "Airport Branch"], description = "name of branch")
    location: constr(min_length=1, max_length=255) = Field(examples=["Rabieh", "Mecca_street"], description = "location of branch")
    size: int = Field(examples=[100, 200], description = "size of branch")
    total_stock: conint(ge=0) = Field(examples=["316", "1523"], description = "total stock of products in branch")

def validate_branch(data: dict):
    try:
        branch = Branches.model_validate(data)
        print(branch)
    except ValidationError as e:
        print("branch invalid")
        for error in e.errors():
            print(error)


class Transactions(BaseModel):
    branch_id: Optional[int] = Field(None, examples=["1", "2"], description = "id of the branch where the product was sold as a foreign key") ## ForeignKey
    customer_id: Optional[int] = Field(None, examples=["1", "2"], description = "id of the customer who made the purchase as a foreign key") # ForeignKey
    total_amount: condecimal(ge=0, decimal_places=2) = Field(examples=["56.92", "30.02"], description = "total amount of the transaction")
    dateOfTransaction: date = Field(examples=["2023-01-01", "2023-01-02"], description = "date of the transaction")
    timeOfTransaction: Any = Field(examples=["10:00", "21:00"], description = "time of the transaction")
    total: condecimal(ge=0, decimal_places=2) = Field(examples=["56.92", "30.02"], description = "total price of the transaction")

def validate_transaction(data: dict):
    try:
        transaction = Transactions.model_validate(data)
        print(transaction)
    except ValidationError as e:
        print("transaction invalid")
        for error in e.errors():
            print(error)


class TransactionDetails(BaseModel):
    transaction_id: Optional[int] = Field(None, description = "id of a transaction as a foreign key")
    product_id: int = Field(examples=["1", "2"], description = "id of a product as a foreign key")  # Foreign key to Product
    quantity: conint(gt=0) = Field(examples=["1", "2"], description = "quantity of a product that was bought")
    price: condecimal(ge=0, decimal_places=2) = Field(examples=["56.92", "30.02"], description = "selling price of a product at the time of transaction")  # Price at time of purchase

def validate_transactionDetails(data: dict):
    try:
        transactionDetails = TransactionDetails.model_validate(data)
        print(transactionDetails)
    except ValidationError as e:
        print("transactionDetails invalid")
        for error in e.errors():
            print(error)

## Apply Pydantic models to database tables (Schema -> Table)


 # Create models (for POST requests) 
 # pass means they're identical to their parent classes, 
 # but we separate them for future flexibility.
 # These are classes for creating new models


class CustomerCreate(Customers):
    pass

class EmployeeCreate(Employees):
    pass

class ProductCreate(Products):
    pass

class BranchCreate(Branches):
    pass

class TransactionCreate(Transactions):
    details: List[TransactionDetails] = Field(
        ...,
        min_items=1,
        description="List of items in the transaction"
    )


# Update models (for PATCH requests)
class CustomerUpdate(Customers):
    name: Optional[constr(min_length=1, max_length=100)] = None
    age: Optional[conint(gt=0, lt=120)] = None
    email: Optional[EmailStr] = None
    membership: Optional[bool] = None

class EmployeeUpdate(Employees):
    name: Optional[constr(min_length=1, max_length=100)] = None
    age: Optional[conint(gt=16, lt=70)] = None
    date_of_end_employment: Optional[date] = None
    role: Optional[Role] = None

class ProductUpdate(Products):
    name: Optional[constr(min_length=1, max_length=100)] = None
    stock: Optional[conint(ge=0)] = None
    sell_price: Optional[condecimal(gt=0, decimal_places=2)] = None
    cost: Optional[condecimal(gt=0, decimal_places=2)] = None
    category_id: Optional[int] = None
    category: Optional[constr(min_length=1, max_length=50)] = None

class BranchUpdate(Branches):
    location: Optional[constr(min_length=1, max_length=200)] = None
    size: Optional[constr(min_length=1, max_length=50)] = None
    total_stock: Optional[conint(ge=0)] = None

# Database models made to read from the database 
class CustomerInDB(Customers):
    id: int

    class Config:
        from_attributes = True

class EmployeeInDB(Employees):
    id: int

    class Config:
        from_attributes = True

class ProductInDB(Products):
    id: int

    class Config:
        from_attributes = True

class BranchInDB(Branches):
    id: int

    class Config:
        from_attributes = True

class TransactionInDB(Transactions):
    id: int

    class Config:
        from_attributes = True

class TransactionDetailInDB(TransactionDetails):
    pass

    class Config:
        from_attributes = True

# Response models
class TransactionResponse(TransactionInDB):
    details: List[TransactionDetailInDB]
    
# Authentication Models
class SignupRequest(BaseModel):
    """Base signup request model"""
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=8)
    age: int = Field(..., gt=0, lt=120)


class CustomerSignupRequest(SignupRequest):
    """Customer signup request model"""
    membership: bool = False


class EmployeeSignupRequest(SignupRequest):
    """Employee signup request model"""
    role: str = Field(..., description="Employee role (ADMIN, CASHIER, etc.)")
    dateOfEmployment: str = Field(..., description="Date of employment (YYYY-MM-DD)")


class LoginRequest(BaseModel):
    """Login request model"""
    email: EmailStr
    password: str
    role: str  # 'customer' or 'admin'


class AuthResponse(BaseModel):
    """Authentication response model"""
    id: int
    name: str
    role: str
    email: EmailStr
    message: str
    access_token: Optional[str] = None
    token_type: Optional[str] = None


class Token(BaseModel):
    """Token response model"""
    access_token: str
    token_type: str


class TokenData(BaseModel):
    """Token data model for decoded tokens"""
    email: Optional[EmailStr] = None
    role: Optional[str] = None
