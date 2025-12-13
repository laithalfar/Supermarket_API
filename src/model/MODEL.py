from datetime import date, time, datetime
from decimal import Decimal
from enum import Enum
from typing import Optional, List, ClassVar
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
    ADMIN: ClassVar[str] = "ADMIN"
    ASSISSTANT_MANAGER: ClassVar[str] = "ASSISSTANT_MANAGER"
    HEAD_OF_BRANCH: ClassVar[str] = "HEAD_OF_BRANCH"
    CUSTOMER_ASSISSTANT: ClassVar[str] = "CUSTOMER_ASSISSTANT"
    STOCKER: ClassVar[str] = "STOCKER"
    CASHIER: ClassVar[str] = "CASHIER"

@dataclass
class Customers(BaseModel):
    name: constr(min_length=1, max_length=100) = Field(examples=["John Doe", "Jane Doe"], min_length=1, description = "name of customer")
    age: conint(gt=0, lt=120) = Field(examples=["7", "8"], min_length=1, max_length=2, description = "age of customer")
    email: EmailStr = Field(examples=["example@gmd.jo"], min_length=1, description = "email address of customer")
    membership: bool = Field(examples=["True", "False"], min_length=1, description = "customer membership status")

def validate_customer(data: dict):
    try:
        customer = customers.model_validate(data)
        print(customer)
    except ValidationError as e:
        print("Customer invalid")
        for error in e.errors():
            print(error)

class Employees(BaseModel):
    name: constr(min_length=1, max_length=100) = Field(examples=["John Doe", "Jane Doe"], min_length=1, description = "name of employee")
    age: conint(gt=16, lt=70) = Field(examples=["7", "8"], min_length=1, max_length=2, description = "age of employee")
    dateOfEmployment: date = Field(examples=["2023-01-01", "2023-01-02"], min_length=1, description = "date of employment of employee")
    dateOfEndOfEmployment: Optional[date] = Field(examples=["2023-01-01", "2023-01-02"], min_length=1, description = "date of the end of employment of an employee which can be empty if employee is stll working")
    email: EmailStr = Field(examples=["example@gmd.jo"], min_length=1, description = "email address of customer", frozen = True)
    role: Role = Field(examples=["HEADOFBRANCH", "CASHIER"], min_length=1, description = "role of employee")

def validate_employee(data: dict):
    try:
        employee = employees.model_validate(data)
        print(employee)
    except ValidationError as e:
        print("Customer invalid")
        for error in e.errors():
            print(error)

@dataclass
class Products(BaseModel):
    name: constr(min_length=1, max_length=100) = Field(examples=["Chicken sandwich", "redbull drink"], min_length=1, description = "Uname of product")
    stock: conint(ge=0) = Field(examples=["30", "1523"], min_length=1, description = "amount of stock for this product")
    sellPrice: condecimal(ge=0) = Field(examples=["30.02", "97.00"], min_length=1, description = "selling price of product in Jordanian Dinar for customers")
    cost: condecimal(ge=0) = Field(examples=["11.20", "40.57"], min_length=1, description = "buying price of product in Jordanian Dinar for supermarket")
    category_id: int = Field(examples=["1", "2"], min_length=1, description = "Unique id of the category of the product") # Main category (e.g., 1 = Food, 2 = Drinks, etc.)
    category: constr(min_length=1, max_length=50) = Field(examples=["healthy Food", "energy Drinks"], min_length=1, description = "name of the category of the product") # Subcategory (e.g., "Meat", "Chicken", "Vegetables")

def validate_product(data: dict):
    try:
        product = Products.model_validate(data)
        print(product)
    except ValidationError as e:
        print("product invalid")
        for error in e.errors():
            print(error)

@dataclass
class Branches(BaseModel):
    location: constr(min_length=1, max_length=200) = Field(examples=["Rabieh", "Mecca_street"], min_length=1, description = "location of branch")
    size: constr(min_length=1, max_length=50) = Field(examples=["big", "small"], min_length=1, description = "size of branch")
    totalStock: conint(ge=0) = Field(examples=["316", "1523"], min_length=3, description = "total stock of products in branch")

def validate_branch(data: dict):
    try:
        branch = Branch.model_validate(data)
        print(branch)
    except ValidationError as e:
        print("branch invalid")
        for error in e.errors():
            print(error)

@dataclass
class Transactions(BaseModel):
    branch_id: int = Field(examples=["1", "2"], min_length=1, description = "id of the branch where the product was sold as a foreign key") ## ForeignKey
    customer_id: int = Field(examples=["1", "2"], min_length=1, description = "id of the customer that bought the product as a foreign key") # ForeignKey
    quantity: int = Field(examples=["1", "2"], min_length=1, min_value=1, description = "quantity of products bought in one trtansaction")
    employee_id: int = Field(examples=["1", "2"], min_length=1, description = "id of the employee that made the transaction as a foreign key") # ForeignKey
    dateOfTransaction: date = Field(examples=["2023-01-01", "2023-01-02"], min_length=1, description = "date of the transaction")
    timeOfTransaction: time = Field(examples=["10:00", "21:00"], min_length=1, max_length=4, description = "time of the transaction")
    total: condecimal(ge=0, decimal_places=2) = Field(examples=["56.92", "30.02"], min_length=1, description = "total price of the transaction")

def validate_transaction(data: dict):
    try:
        transaction = Transaction.model_validate(data)
        print(transaction)
    except ValidationError as e:
        print("transaction invalid")
        for error in e.errors():
            print(error)

@dataclass
class TransactionDetails(BaseModel):
    product_id: int = Field(examples=["1", "2"], min_length=1, description = "id of a product as a foreign key")  # Foreign key to Product
    quantity: conint(gt=0) = Field(examples=["1", "2"], min_length=1, description = "quantity of a product that was bought")
    price: condecimal(ge=0, decimal_places=2) = Field(examples=["56.92", "30.02"], min_length=1, description = "selling price of a product at the time of transaction")  # Price at time of purchase

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



# These are classes for creating new models
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

# Database models (for responses)
# So these give the structure for databases when we query them
class CustomerInDB(Customers):
    id: int

    class Config:
        orm_mode = True

class EmployeeInDB(Employees):
    id: int

    class Config:
        orm_mode = True

class ProductInDB(Products):
    id: int

    class Config:
        orm_mode = True

class BranchInDB(Branches):
    id: int

    class Config:
        orm_mode = True

class TransactionInDB(Transactions):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True

class TransactionDetailInDB(TransactionDetails):
    transaction_id: int

    class Config:
        orm_mode = True

# Response models
class TransactionResponse(TransactionInDB):
    details: List[TransactionDetailInDB]





    



    
