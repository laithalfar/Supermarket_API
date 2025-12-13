import os
import logging
from contextlib import contextmanager
from typing import Any, Dict, List, Optional, Type, TypeVar, Union
from mysql.connector import Error, pooling
from pymysql.cursors import DictCursor
from pydantic import BaseModel, ValidationError

# Import models
from src.model.MODEL import (
    Customers as CustomerModel,
    Employees as EmployeeModel,
    Products as ProductModel,
    Branches as BranchModel,
    Transactions as TransactionModel,
    TransactionDetails as TransactionDetailsModel
)

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Database configuration
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", "0798628195Far"),
    "database": os.getenv("DB_NAME", "Supermarket"),
}

POOL_NAME = os.getenv("DB_POOL_NAME", "supermarket_pool")
POOL_SIZE = int(os.getenv("DB_POOL_SIZE", "5"))
_connection_pool = None

def get_connection_pool():
    """Initialize and return a connection pool."""
    global _connection_pool
    if _connection_pool is None:
        try:
            _connection_pool = pooling.MySQLConnectionPool(
                pool_name=POOL_NAME,
                pool_size=POOL_SIZE,
                pool_reset_session=True,
                **DB_CONFIG,
            )
            logger.info("Database connection pool initialized")
        except Error as err:
            logger.error("Failed to initialize database pool: %s", err)
            raise RuntimeError(f"Failed to initialize database pool: {err}") from err
    return _connection_pool

@contextmanager
def get_connection():
    """Context manager for database connections."""
    conn = None
    try:
        pool = get_connection_pool()
        conn = pool.get_connection()
        logger.debug("Acquired database connection from pool")
        yield conn
    except Error as e:
        logger.error("Database connection error: %s", e)
        raise
    finally:
        if conn and conn.is_connected():
            conn.close()
            logger.debug("Database connection returned to pool")

@contextmanager
def get_cursor(dictionary: bool = True, **kwargs):
    """Context manager for database cursors."""
    with get_connection() as conn:
        cursor = None
        try:
            cursor = conn.cursor(dictionary=dictionary, **kwargs)
            yield cursor
            conn.commit()
        except Error as e:
            conn.rollback()
            logger.error("Database operation failed: %s", e)
            raise
        finally:
            if cursor:
                cursor.close()

def execute_write(query: str, params: tuple = None) -> int:
    """Execute a write query and return the last row ID."""
    with get_cursor() as cursor:
        cursor.execute(query, params or ())
        return cursor.lastrowid

def execute_read(query: str, params: tuple = None, model: Type[BaseModel] = None) -> Union[Dict, BaseModel]:
    """Execute a read query and optionally map to a Pydantic model."""
    with get_cursor() as cursor:
        cursor.execute(query, params or ())
        result = cursor.fetchone()
        if result and model:
            try:
                return model.model_validate(result)
            except ValidationError as e:
                logger.error("Validation error: %s", e)
                raise ValueError(f"Data validation error: {e}") from e
        return result

def execute_read_all(query: str, params: tuple = None, model: Type[BaseModel] = None) -> List[Union[Dict, BaseModel]]:
    """Execute a read query that returns multiple rows and optionally map to Pydantic models."""
    with get_cursor() as cursor:
        cursor.execute(query, params or ())
        results = cursor.fetchall()
        if results and model:
            try:
                return [model.model_validate(row) for row in results]
            except ValidationError as e:
                logger.error("Validation error: %s", e)
                raise ValueError(f"Data validation error: {e}") from e
        return results

def create_entity(table: str, data: Dict[str, Any], model: Type[BaseModel]) -> int:
    """
    Generic function to create a new entity with validation.
    
    Args:
        table: Name of the table
        data: Dictionary of fields and values
        model: Pydantic model for validation
        
    Returns:
        int: The ID of the created entity
        
    Raises:
        ValueError: If validation fails
        RuntimeError: If database operation fails
    """
    try:
        # Validate input data
        entity = model.model_validate(data)
        entity_data = entity.model_dump()
        
        # Prepare query
        columns = ', '.join(entity_data.keys())
        placeholders = ', '.join(['%s'] * len(entity_data))
        values = tuple(entity_data.values())
        
        query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
        
        # Execute insert
        entity_id = execute_write(query, values)
        logger.info("Created %s with ID: %s", table, entity_id)
        return entity_id
        
    except ValidationError as e:
        logger.error("Validation failed for %s creation: %s", table, e)
        raise ValueError(f"Invalid {table} data: {e}") from e
    except Error as e:
        logger.error("Failed to create %s: %s", table, e)
        raise RuntimeError(f"Database error while creating {table}: {e}") from e

def update_entity(
    table: str, 
    entity_id: int, 
    updates: Dict[str, Any], 
    model: Type[BaseModel],
    id_column: str = "id"
) -> bool:
    """
    Generic function to update an entity with validation.
    
    Args:
        table: Name of the table
        entity_id: ID of the entity to update
        updates: Dictionary of fields to update
        model: Pydantic model for validation
        id_column: Name of the ID column (default: 'id')
        
    Returns:
        bool: True if update was successful, False otherwise
    """
    if not updates:
        logger.warning("No update fields provided for %s %s", table, entity_id)
        return False

    try:
        # Get existing data
        existing = execute_read(
            f"SELECT * FROM {table} WHERE {id_column} = %s",
            (entity_id,)
        )
        
        if not existing:
            logger.error("%s not found with %s: %s", table, id_column, entity_id)
            return False

        # Merge updates with existing data
        entity_data = {**existing, **updates}
        
        try:
            # Validate using Pydantic model
            model.model_validate(entity_data)
        except ValidationError as e:
            logger.error("Validation failed for %s update: %s", table, e)
            raise ValueError(f"Invalid {table} data: {e}") from e

        # Build dynamic update query
        update_fields = []
        values = []
        
        for field, value in updates.items():
            if value is not None and field != id_column:  # Don't update the ID
                update_fields.append(f"{field} = %s")
                values.append(value)
                
        if not update_fields:
            logger.warning("No valid fields to update for %s %s", table, entity_id)
            return False

        # Add entity_id for WHERE clause
        values.append(entity_id)
        
        # Execute update
        query = f"UPDATE {table} SET {', '.join(update_fields)} WHERE {id_column} = %s"
        execute_write(query, values)
        
        logger.info("Successfully updated %s with %s: %s", table, id_column, entity_id)
        return True

    except Error as e:
        logger.error("Failed to update %s %s: %s", table, entity_id, e)
        raise RuntimeError(f"Database error while updating {table}: {e}") from e

def delete_entity(table: str, entity_id: int, id_column: str = "id") -> bool:
    """
    Generic function to delete an entity by ID.
    
    Args:
        table: Name of the table
        entity_id: ID of the entity to delete
        id_column: Name of the ID column (default: 'id')
        
    Returns:
        bool: True if deletion was successful, False otherwise
    """
    try:
        # First check if the entity exists
        exists = execute_read(
            f"SELECT 1 FROM {table} WHERE {id_column} = %s",
            (entity_id,)
        )
        
        if not exists:
            logger.warning("%s with %s %s not found", table, id_column, entity_id)
            return False
            
        # Delete the entity
        execute_write(
            f"DELETE FROM {table} WHERE {id_column} = %s",
            (entity_id,)
        )
        
        logger.info("Deleted %s with %s: %s", table, id_column, entity_id)
        return True
        
    except Error as e:
        logger.error("Failed to delete %s %s: %s", table, entity_id, e)
        raise RuntimeError(f"Database error while deleting {table}: {e}") from e

# Specific CRUD operations using the generic functions
def create_customer(customer_data: Dict[str, Any]) -> int:
    """Create a new customer with validation."""
    return create_entity("CUSTOMER", customer_data, CustomerModel)

def get_customer(customer_id: int) -> Optional[Dict[str, Any]]:
    """Get a customer by ID with validation."""
    return execute_read("SELECT * FROM CUSTOMER WHERE id = %s", (customer_id,), CustomerModel)

def update_customer(customer_id: int, **updates) -> bool:
    """Update customer details with validation."""
    return update_entity("CUSTOMER", customer_id, updates, CustomerModel)

def delete_customer(customer_id: int) -> bool:
    """Delete a customer by ID."""
    return delete_entity("CUSTOMER", customer_id)

def create_employee(employee_data: Dict[str, Any]) -> int:
    """Create a new employee with validation."""
    return create_entity("EMPLOYEE", employee_data, EmployeeModel)

def get_employee(employee_id: int) -> Optional[Dict[str, Any]]:
    """Get an employee by ID with validation."""
    return execute_read("SELECT * FROM EMPLOYEE WHERE id = %s", (employee_id,), EmployeeModel)

def update_employee(employee_id: int, **updates) -> bool:
    """Update employee details with validation."""
    return update_entity("EMPLOYEE", employee_id, updates, EmployeeModel)

def delete_employee(employee_id: int) -> bool:
    """Delete an employee by ID."""
    return delete_entity("EMPLOYEE", employee_id)

def create_product(product_data: Dict[str, Any]) -> int:
    """Create a new product with validation."""
    return create_entity("PRODUCT", product_data, ProductModel)

def get_product(product_id: int) -> Optional[Dict[str, Any]]:
    """Get a product by ID with validation."""
    return execute_read("SELECT * FROM PRODUCT WHERE id = %s", (product_id,), ProductModel)

def update_product(product_id: int, **updates) -> bool:
    """Update product details with validation."""
    return update_entity("PRODUCT", product_id, updates, ProductModel)

def delete_product(product_id: int) -> bool:
    """Delete a product by ID."""
    return delete_entity("PRODUCT", product_id)

def create_branch(branch_data: Dict[str, Any]) -> int:
    """Create a new branch with validation."""
    return create_entity("BRANCH", branch_data, BranchModel)

def get_branch(branch_id: int) -> Optional[Dict[str, Any]]:
    """Get a branch by ID with validation."""
    return execute_read("SELECT * FROM BRANCH WHERE id = %s", (branch_id,), BranchModel)

def update_branch(branch_id: int, **updates) -> bool:
    """Update branch details with validation."""
    return update_entity("BRANCH", branch_id, updates, BranchModel)

def delete_branch(branch_id: int) -> bool:
    """Delete a branch by ID."""
    return delete_entity("BRANCH", branch_id)

def create_transaction(transaction_data: Dict[str, Any]) -> int:
    """Create a new transaction with validation."""
    return create_entity("TRANSACTION", transaction_data, TransactionModel)

def get_transaction(transaction_id: int) -> Optional[Dict[str, Any]]:
    """Get a transaction by ID with validation."""
    return execute_read("SELECT * FROM TRANSACTION WHERE id = %s", (transaction_id,), TransactionModel)

def update_transaction(transaction_id: int, **updates) -> bool:
    """Update transaction details with validation."""
    return update_entity("TRANSACTION", transaction_id, updates, TransactionModel)

def delete_transaction(transaction_id: int) -> bool:
    """Delete a transaction by ID."""
    return delete_entity("TRANSACTION", transaction_id)

def create_transaction_details(details_data: Dict[str, Any]) -> int:
    """Create new transaction details with validation."""
    return create_entity("TRANSACTIONDETAILS", details_data, TransactionDetailsModel, id_column="transaction_id")

def get_transaction_details(transaction_id: int) -> Optional[Dict[str, Any]]:
    """Get transaction details by transaction ID with validation."""
    return execute_read(
        "SELECT * FROM TRANSACTIONDETAILS WHERE transaction_id = %s", 
        (transaction_id,), 
        TransactionDetailsModel
    )

def update_transaction_details(transaction_id: int, **updates) -> bool:
    """Update transaction details with validation."""
    return update_entity(
        "TRANSACTIONDETAILS", 
        transaction_id, 
        updates, 
        TransactionDetailsModel,
        id_column="transaction_id"
    )

def delete_transaction_details(transaction_id: int) -> bool:
    """Delete transaction details by transaction ID."""
    return delete_entity("TRANSACTIONDETAILS", transaction_id, id_column="transaction_id")

# CREATE: Add a new transaction
def create_transaction(id, branch_id, customer_id, quantity, employee_id, date, time, total):
    execute_write(
        "INSERT INTO TRANSACTION (id, branch_id, customer_id, quantity, employee_id, date, time, total) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
        (id, branch_id, customer_id, quantity, employee_id, date, time, total),
    )
    print(f"transaction '{id}' added successfully!")


# CREATE: Add new TransactionDetails
def create_transactionDetails(transaction_id, product_id, quantity, price):
    execute_write(
        "INSERT INTO TRANSACTIONDETAILS (transaction_id, product_id, quantity, price) VALUES (%s, %s, %s, %s)",
        (transaction_id, product_id, quantity, price),
    )
    print(f"Transaction details for transaction '{transaction_id}' added successfully!")


# Read Functions for different tables in supermarket database

# READ: Get a customer by ID
def read_customer(customer_id):
    query = "SELECT * FROM Customer WHERE id = %s"
    return execute_read(query, (customer_id,), dictionary=True)


# READ: Get an employee by ID
def read_employee(employee_id):
    query = "SELECT * FROM EMPLOYEE WHERE id = %s"
    return execute_read(query, (employee_id,), dictionary=True)


# READ: Get a product by ID
def read_product(product_id):
    query = "SELECT * FROM PRODUCT WHERE id = %s"
    return execute_read(query, (product_id,), dictionary=True)


# READ: Get a branch by ID
def read_branch(branch_id):
    query = "SELECT * FROM BRANCH WHERE id = %s"
    return execute_read(query, (branch_id,), dictionary=True)


# READ: Get a transaction by ID
def read_transaction(transaction_id):
    query = "SELECT * FROM TRANSACTION WHERE id = %s"
    return execute_read(query, (transaction_id,), dictionary=True)


# READ: Get transaction details by transaction_ID
def read_transactionDetails(transaction_id):
    query = "SELECT * FROM TRANSACTIONDETAILS WHERE transaction_id = %s"
    return execute_read(query, (transaction_id,), dictionary=True)


# UPDATE: Update a customer's details
def update_customer(customer_id, name=None, age=None, email=None, membership=None):
    # Build dynamic query
    updates = []
    values = []

    if name is not None:
        updates.append("name = %s")
        values.append(name)
    if age is not None:
        updates.append("age = %s")
        values.append(age)
    if email is not None:
        updates.append("email = %s")
        values.append(email)
    if membership is not None:
        updates.append("membership = %s")
        values.append(membership)

    if not updates:
        print("No fields to update")
        return

    values.append(customer_id)
    query = f"UPDATE CUSTOMER SET {', '.join(updates)} WHERE id = %s"
    execute_write(query, values)
    print(f"Customer with ID {customer_id} updated successfully!")


# UPDATE: Update a employee's details
def update_employee(employee_id, name=None, age=None, dateOfEmployment=None, dateOfEndOfEmployment=None, email=None, role=None):
    # Build dynamic query
    updates = []
    values = []

    if name is not None:
        updates.append("name = %s")
        values.append(name)
    if age is not None:
        updates.append("age = %s")
        values.append(age)
    if email is not None:
        updates.append("email = %s")
        values.append(email)
    if dateOfEmployment is not None:
        updates.append("dateOfEmployment = %s")
        values.append(dateOfEmployment)
    if dateOfEndOfEmployment is not None:
        updates.append("dateOfEndOfEmployment = %s")
        values.append(dateOfEndOfEmployment)
    if role is not None:
        updates.append("role = %s")
        values.append(role)

    if not updates:
        print("No fields to update")
        return

    values.append(employee_id)
    query = f"UPDATE EMPLOYEE SET {', '.join(updates)} WHERE id = %s"
    execute_write(query, values)
    print(f"Employee with ID {employee_id} updated successfully!")


def update_product(product_id, name=None, stock=None, sellPrice=None, cost=None, category_id=None, category=None):
    # Build dynamic query
    updates = []
    values = []

    if name is not None:
        updates.append("name = %s")
        values.append(name)
    if stock is not None:
        updates.append("stock = %s")
        values.append(stock)
    if sellPrice is not None:
        updates.append("sellPrice = %s")
        values.append(sellPrice)
    if cost is not None:
        updates.append("cost = %s")
        values.append(cost)
    if category_id is not None:
        updates.append("category_id = %s")
        values.append(category_id)
    if category is not None:
        updates.append("category = %s")
        values.append(category)

    if not updates:
        print("No fields to update")
        return

    values.append(product_id)
    query = f"UPDATE PRODUCT SET {', '.join(updates)} WHERE id = %s"
    execute_write(query, values)
    print(f"Product with ID {product_id} updated successfully!")


def update_branch(branch_id, location=None, size=None, totalStock=None):
    # Build dynamic query
    updates = []
    values = []

    if location is not None:
        updates.append("location = %s")
        values.append(location)
    if size is not None:
        updates.append("size = %s")
        values.append(size)
    if totalStock is not None:
        updates.append("totalStock = %s")
        values.append(totalStock)

    if not updates:
        print("No fields to update")
        return

    values.append(branch_id)
    query = f"UPDATE BRANCH SET {', '.join(updates)} WHERE id = %s"
    execute_write(query, values)
    print(f"Branch with ID {branch_id} updated successfully!")


def update_transaction(transaction_id, branch_id=None, customer_id=None, quantity=None, employee_id=None, date=None, time=None, total=None):
    # Build dynamic query
    updates = []
    values = []

    if branch_id is not None:
        updates.append("branch_id = %s")
        values.append(branch_id)
    if customer_id is not None:
        updates.append("customer_id = %s")
        values.append(customer_id)
    if quantity is not None:
        updates.append("quantity = %s")
        values.append(quantity)
    if employee_id is not None:
        updates.append("employee_id = %s")
        values.append(employee_id)
    if date is not None:
        updates.append("date = %s")
        values.append(date)
    if time is not None:
        updates.append("time = %s")
        values.append(time)
    if total is not None:
        updates.append("total = %s")
        values.append(total)

    if not updates:
        print("No fields to update")
        return

    values.append(transaction_id)
    query = f"UPDATE TRANSACTION SET {', '.join(updates)} WHERE id = %s"
    execute_write(query, values)
    print(f"Transaction with ID {transaction_id} updated successfully!")


def update_transactionDetails(transaction_id, product_id=None, quantity=None, price=None):
    # Build dynamic query
    updates = []
    values = []

    if product_id is not None:
        updates.append("product_id = %s")
        values.append(product_id)
    if quantity is not None:
        updates.append("quantity = %s")
        values.append(quantity)
    if price is not None:
        updates.append("price = %s")
        values.append(price)

    if not updates:
        print("No fields to update")
        return

    values.append(transaction_id)
    query = f"UPDATE TRANSACTIONDETAILS SET {', '.join(updates)} WHERE transaction_id = %s"
    execute_write(query, values)
    print(f"Transaction details for transaction {transaction_id} updated successfully!")


# DELETE: Remove a customer by ID
def delete_customer(customer_id):
    query = "DELETE FROM CUSTOMER WHERE id = %s"
    execute_write(query, (customer_id,))
    print(f"Customer with ID {customer_id} deleted successfully!")


# DELETE: Remove a customer by ID
def delete_employee(employee_id):
    query = "DELETE FROM EMPLOYEE WHERE id = %s"
    execute_write(query, (employee_id,))
    print(f"Employee with ID {employee_id} deleted successfully!")


# DELETE: Remove a customer by ID
def delete_product(product_id):
    query = "DELETE FROM PRODUCT WHERE id = %s"
    execute_write(query, (product_id,))
    print(f"Product with ID {product_id} deleted successfully!")


# DELETE: Remove a customer by ID
def delete_branch(branch_id):
    query = "DELETE FROM BRANCH WHERE id = %s"
    execute_write(query, (branch_id,))
    print(f"Branch with ID {branch_id} deleted successfully!")


# DELETE: Remove a customer by ID
def delete_transaction(transaction_id):
    query = "DELETE FROM TRANSACTION WHERE id = %s"
    execute_write(query, (transaction_id,))
    print(f"Transaction with ID {transaction_id} deleted successfully!")


# DELETE: Remove a customer by ID
def delete_transactionDetails(transaction_id):
    query = "DELETE FROM TRANSACTIONDETAILS WHERE transaction_id = %s"
    execute_write(query, (transaction_id,))
    print(f"Transaction details with ID {transaction_id} deleted successfully!")

# Use the new database
#mycursor.execute("USE supermarket")

#customers

# mycursor.execute( """
#                  CREATE TABLE IF NOT EXISTS CUSTOMER (
#                  id INT AUTO_INCREMENT PRIMARY KEY,
#                  name VARCHAR(255),
#                  age INT,
#                  email VARCHAR(255),
#                  membership BOOLEAN
#                  )
#                  """) 

# #employees
# mycursor.execute( """
#                  CREATE TABLE IF NOT EXISTS EMPLOYEES(
#                  id INT AUTO_INCREMENT PRIMARY KEY,
#                  name: VARCHAR(255),
#                  age: INT, 
#                  dateOfEmployment: VARCHAR(255),
#                  dateOfEndOfEmployment: VARCHAR(255),
#                  email: VARCHAR(255),
#                  role: VARCHAR(255)
#                  )
#                  """)


# #product
# mycursor.execute( """
#                  CREATE TABLE IF NOT EXISTS PRODUCT (
#                  id: INT AUTO_INCREMENT PRIMARY KEY,
#                  name: VARCHAR(255),
#                  stock: INT,
#                  sellPrice: FLOAT,
#                  cost: FLOAT, 
#                  category_id: INT,
#                  category: VARCHAR(255) 
#                  )
#                  """)

# #branch
# mycursor.execute( """
#                  CREATE TABLE IF NOT EXISTS BRANCH (
#                  id: INT AUTO_INCREMENT PRIMARY KEY,
#                  location: VARCHAR(255),
#                  size: VARCHAR(255),
#                  totalStock: INT
#                  )
#                  """)

# #transaction
# mycursor.execute( """
#                  CREATE TABLE IF NOT EXISTS TRANSACTION (
#                  id: INT AUTO_INCREMENT PRIMARY KEY,
#                  branch_id: INT FOREIGN KEY,
#                  customer_id: INT FOREIGN KEY,
#                  quantity: INT,
#                  employee_id: INT FOREIGN KEY,
#                  date: DATE,
#                  time: TIME,
#                  total: FLOAT
#                  )
#                  """)

# #TransactionDetails
# mycursor.execute( """
#                  CREATE TABLE IF NOT EXISTS TRANSACTION_DETAILS (            
#                  transaction_id: INT FOREIGN_KEY,
#                  product_id: INT FOREIGN_KEY,
#                  quantity: INT,
#                  price: FLOAT
#                  )
#                  """)

# for db in mycursor:
#     print(db)