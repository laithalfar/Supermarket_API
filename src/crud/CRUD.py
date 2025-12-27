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
    TransactionDetails as TransactionDetailsModel,
    CustomerInDB,
    EmployeeInDB,
    ProductInDB,
    BranchInDB,
    TransactionInDB,
    TransactionDetailInDB
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

def execute_write(query: str, params: Optional[tuple] = None) -> int:
    """Execute a write query and return the last row ID."""
    with get_cursor() as cursor:
        cursor.execute(query, params or ())
        return cursor.lastrowid

def execute_read(query: str, params: Optional[tuple] = None, theModel: Optional[Type[BaseModel]] = None) -> Union[Dict, BaseModel, None]:
    """Execute a read query and optionally map to a Pydantic model."""
    with get_cursor() as cursor:
        cursor.execute(query, params or ())
        result = cursor.fetchone()
        if result and theModel:
            try:
                # Explicitly cast to BaseModel to satisfy type checker
                return theModel.model_validate(result)
            except ValidationError as e:
                logger.error("Validation error: %s", e)
                raise ValueError(f"Data validation error: {e}") from e
        return result

def execute_read_all(query: str, params: Optional[tuple] = None, theModel: Optional[Type[BaseModel]] = None) -> List[Any]:
    """Execute a read query that returns multiple rows and optionally map to Pydantic models."""
    with get_cursor() as cursor:
        cursor.execute(query, params or ())
        results = cursor.fetchall()
        if results and theModel:
            try:
                return [theModel.model_validate(row) for row in results]
            except ValidationError as e:
                logger.error("Validation error: %s", e)
                raise ValueError(f"Data validation error: {e}") from e
        return results

def create_entity(table: str, data: Dict[str, Any], theModel: Type[BaseModel]) -> int:
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
        entity = theModel.model_validate(data)
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
    theModel: Type[BaseModel],
    id_column: str = "id"
) -> bool:
    """
    Generic function to update an entity with validation.
    
    Args:
        table: Name of the table
        entity_id: ID of the entity to update
        updates: Dictionary of fields to update
        model: Pydantic theModel for validation
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
            theModel.model_validate(entity_data)
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
        execute_write(query, tuple(values))
        
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
def create_customer(customer_data: Dict[str, Any]) -> Any:
    """Create a new customer and return the full object."""
    customer_id = create_entity("CUSTOMERS", customer_data, CustomerModel)
    return get_customer(customer_id)

def get_customer(customer_id: int) -> Any:
    """Get a customer by ID with validation."""
    return execute_read("SELECT * FROM CUSTOMERS WHERE id = %s", (customer_id,), CustomerInDB)

def update_customer(customer_id: int, updates: Dict[str, Any]) -> Any:
    """Update customer details and return the updated object."""
    if update_entity("CUSTOMERS", customer_id, updates, CustomerModel):
        return get_customer(customer_id)
    return None

def delete_customer(customer_id: int) -> bool:
    """Delete a customer by ID."""
    return delete_entity("CUSTOMERS", customer_id)

def create_employee(employee_data: Dict[str, Any]) -> Any:
    """Create a new employee and return the full object."""
    employee_id = create_entity("EMPLOYEES", employee_data, EmployeeModel)
    return get_employee(employee_id)

def get_employee(employee_id: int) -> Any:
    """Get an employee by ID with validation."""
    return execute_read("SELECT * FROM EMPLOYEES WHERE id = %s", (employee_id,), EmployeeInDB)

def get_employees(skip: int = 0, limit: int = 100, **filters) -> List[Any]:
    """Get all employees with filters."""
    query = "SELECT * FROM EMPLOYEES"
    params = []
    if filters:
        filter_str = " AND ".join([f"{k} = %s" for k in filters.keys()])
        query += f" WHERE {filter_str}"
        params = list(filters.values())
    query += f" LIMIT %s OFFSET %s"
    params.extend([limit, skip])
    return execute_read_all(query, tuple(params), EmployeeInDB)

def update_employee(employee_id: int, updates: Dict[str, Any]) -> Any:
    """Update employee details and return the updated object."""
    if update_entity("EMPLOYEES", employee_id, updates, EmployeeModel):
        return get_employee(employee_id)
    return None

def delete_employee(employee_id: int) -> bool:
    """Delete an employee by ID."""
    return delete_entity("EMPLOYEES", employee_id)

def create_product(product_data: Dict[str, Any]) -> Any:
    """Create a new product and return the full object."""
    product_id = create_entity("PRODUCTS", product_data, ProductModel)
    return get_product(product_id)

def get_product(product_id: int) -> Any:
    """Get a product by ID with validation."""
    return execute_read("SELECT * FROM PRODUCTS WHERE id = %s", (product_id,), ProductInDB)

def get_products(skip: int = 0, limit: int = 100, **filters) -> List[Any]:
    """Get all products with filters."""
    query = "SELECT * FROM PRODUCTS"
    params = []
    # Simplified filter handling for demonstration
    # In a real app, you'd handle __gte, __lte etc.
    if filters:
        filter_parts = []
        for k, v in filters.items():
            if k.endswith("__gte"):
                filter_parts.append(f"{k[:-5]} >= %s")
            elif k.endswith("__lte"):
                filter_parts.append(f"{k[:-5]} <= %s")
            else:
                filter_parts.append(f"{k} = %s")
            params.append(v)
        query += f" WHERE {' AND '.join(filter_parts)}"
    
    query += f" LIMIT %s OFFSET %s"
    params.extend([limit, skip])
    return execute_read_all(query, tuple(params), ProductInDB)

def update_product(product_id: int, updates: Dict[str, Any]) -> Any:
    """Update product details and return the updated object."""
    if update_entity("PRODUCTS", product_id, updates, ProductModel):
        return get_product(product_id)
    return None

def delete_product(product_id: int) -> bool:
    """Delete a product by ID."""
    return delete_entity("PRODUCTS", product_id)

def create_branch(branch_data: Dict[str, Any]) -> Any:
    """Create a new branch and return the full object."""
    branch_id = create_entity("BRANCHES", branch_data, BranchModel)
    return get_branch(branch_id)

def get_branch(branch_id: int) -> Any:
    """Get a branch by ID with validation."""
    return execute_read("SELECT * FROM BRANCHES WHERE id = %s", (branch_id,), BranchInDB)

def get_branches(skip: int = 0, limit: int = 100, **filters) -> List[Any]:
    """Get all branches with filters."""
    query = "SELECT * FROM BRANCHES"
    params = []
    if filters:
        filter_str = " AND ".join([f"{k} = %s" for k in filters.keys()])
        query += f" WHERE {filter_str}"
        params = list(filters.values())
    query += f" LIMIT %s OFFSET %s"
    params.extend([limit, skip])
    return execute_read_all(query, tuple(params), BranchInDB)

def update_branch(branch_id: int, updates: Dict[str, Any]) -> Any:
    """Update branch details and return the updated object."""
    if update_entity("BRANCHES", branch_id, updates, BranchModel):
        return get_branch(branch_id)
    return None

def delete_branch(branch_id: int) -> bool:
    """Delete a branch by ID."""
    return delete_entity("BRANCHES", branch_id)

def create_transaction(transaction_data: Dict[str, Any]) -> Any:
    """Create a new transaction and return the full object."""
    # Note: Full implementation would handle nested details, 
    # but for now keeping it compatible with current create_entity logic.
    transaction_id = create_entity("TRANSACTIONS", transaction_data, TransactionModel)
    return get_transaction(transaction_id)

def get_transaction(transaction_id: int) -> Any:
    """Get a transaction by ID with validation."""
    return execute_read("SELECT * FROM TRANSACTIONS WHERE id = %s", (transaction_id,), TransactionInDB)

def get_transactions(skip: int = 0, limit: int = 100, **filters) -> List[Any]:
    """Get all transactions with filters."""
    query = "SELECT * FROM TRANSACTIONS"
    params = []
    if filters:
        filter_parts = []
        for k, v in filters.items():
            if k.endswith("__gte"):
                filter_parts.append(f"{k[:-5]} >= %s")
            elif k.endswith("__lte"):
                filter_parts.append(f"{k[:-5]} <= %s")
            else:
                filter_parts.append(f"{k} = %s")
            params.append(v)
        query += f" WHERE {' AND '.join(filter_parts)}"
    
    query += f" LIMIT %s OFFSET %s"
    params.extend([limit, skip])
    return execute_read_all(query, tuple(params), TransactionInDB)

def update_transaction(transaction_id: int, updates: Dict[str, Any]) -> Any:
    """Update transaction details and return the updated object."""
    if update_entity("TRANSACTIONS", transaction_id, updates, TransactionModel):
        return get_transaction(transaction_id)
    return None

def delete_transaction(transaction_id: int) -> bool:
    """Delete a transaction by ID."""
    return delete_entity("TRANSACTIONS", transaction_id)

def get_transaction_details(transaction_id: int) -> List[BaseModel]:
    """Get transaction details by transaction ID."""
    query = "SELECT * FROM TRANSACTION_DETAILS WHERE transaction_id = %s"
    return execute_read_all(query, (transaction_id,), TransactionDetailInDB)

