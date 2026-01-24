import logging
from typing import Any, Dict, List, Optional, Type, Union, Sequence
from sqlalchemy.orm import Session
from sqlalchemy import select, update as sqlalchemy_update, delete as sqlalchemy_delete, and_
from pydantic import BaseModel, ValidationError

# Import ORM models
from src.model.orm import Customer, Employee, Product, Branch, Transaction, TransactionDetail
from src.database import SessionLocal

# Import Pydantic models for validation/return types
from src.model.MODEL import (
    CustomerInDB,
    EmployeeInDB,
    ProductInDB,
    BranchInDB,
    TransactionInDB,
    TransactionDetailInDB,
    Customers as CustomerModel,
    Employees as EmployeeModel,
    Products as ProductModel,
    Branches as BranchModel,
    Transactions as TransactionModel
)

# Set up logging
logger = logging.getLogger(__name__)

# Generic CRUD Helpers using ORM
def get_entity_by_id(db: Session, model: Any, entity_id: int):
    return db.get(model, entity_id)

def create_entity(db: Session, model: Any, data: Dict[str, Any]):
    # Hash password if present
    if "password" in data:
        from src.utils.security import hash_password
        data["password"] = hash_password(data["password"])
    
    db_item = model(**data)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

def update_entity(db: Session, model: Any, entity_id: int, updates: Dict[str, Any]):
    # Hash password if present
    if "password" in updates:
        from src.utils.security import hash_password
        updates["password"] = hash_password(updates["password"])
        
    db_item = get_entity_by_id(db, model, entity_id)
    if not db_item:
        return None
    
    for key, value in updates.items():
        setattr(db_item, key, value)
    
    db.commit()
    db.refresh(db_item)
    return db_item

def delete_entity(db: Session, model: Any, entity_id: int):
    db_item = get_entity_by_id(db, model, entity_id)
    if not db_item:
        return False
    db.delete(db_item)
    db.commit()
    return True

# Specific CRUD operations

# --- CUSTOMERS ---
def create_customer(db: Session, customer_data: Dict[str, Any]) -> Customer:
    return create_entity(db, Customer, customer_data)

def get_customer(db: Session, customer_id: int) -> Optional[Customer]:
    return get_entity_by_id(db, Customer, customer_id)

def get_customers(db: Session, skip: int = 0, limit: int = 100, **filters) -> List[Customer]:
    query = select(Customer)
    if filters:
        filter_clauses = [getattr(Customer, k) == v for k, v in filters.items() if hasattr(Customer, k)]
        query = query.where(and_(*filter_clauses))
    return list(db.execute(query.offset(skip).limit(limit)).scalars().all())

def update_customer(db: Session, customer_id: int, updates: Dict[str, Any]) -> Optional[Customer]:
    return update_entity(db, Customer, customer_id, updates)

def delete_customer(db: Session, customer_id: int) -> bool:
    return delete_entity(db, Customer, customer_id)


# --- EMPLOYEES ---
def create_employee(db: Session, employee_data: Dict[str, Any]) -> Employee:
    return create_entity(db, Employee, employee_data)

def get_employee(db: Session, employee_id: int) -> Optional[Employee]:
    return get_entity_by_id(db, Employee, employee_id)

def get_employees(db: Session, skip: int = 0, limit: int = 100, **filters) -> List[Employee]:
    query = select(Employee)
    if filters:
        filter_clauses = [getattr(Employee, k) == v for k, v in filters.items() if hasattr(Employee, k)]
        query = query.where(and_(*filter_clauses))
    return list(db.execute(query.offset(skip).limit(limit)).scalars().all())

def update_employee(db: Session, employee_id: int, updates: Dict[str, Any]) -> Optional[Employee]:
    return update_entity(db, Employee, employee_id, updates)

def delete_employee(db: Session, employee_id: int) -> bool:
    return delete_entity(db, Employee, employee_id)


# --- PRODUCTS ---
def create_product(db: Session, product_data: Dict[str, Any]) -> Product:
    return create_entity(db, Product, product_data)

def get_product(db: Session, product_id: int) -> Optional[Product]:
    return get_entity_by_id(db, Product, product_id)

def get_products(db: Session, skip: int = 0, limit: int = 100, **filters) -> List[Product]:
    query = select(Product)
    filter_parts = []
    for k, v in filters.items():
        if k.endswith("__gte"):
            field = k[:-5]
            if hasattr(Product, field):
                filter_parts.append(getattr(Product, field) >= v)
        elif k.endswith("__lte"):
            field = k[:-5]
            if hasattr(Product, field):
                filter_parts.append(getattr(Product, field) <= v)
        else:
            if hasattr(Product, k):
                filter_parts.append(getattr(Product, k) == v)
    
    if filter_parts:
        query = query.where(and_(*filter_parts))
        
    return list(db.execute(query.offset(skip).limit(limit)).scalars().all())

def update_product(db: Session, product_id: int, updates: Dict[str, Any]) -> Optional[Product]:
    return update_entity(db, Product, product_id, updates)

def delete_product(db: Session, product_id: int) -> bool:
    return delete_entity(db, Product, product_id)


# --- BRANCHES ---
def create_branch(db: Session, branch_data: Dict[str, Any]) -> Branch:
    return create_entity(db, Branch, branch_data)

def get_branch(db: Session, branch_id: int) -> Optional[Branch]:
    return get_entity_by_id(db, Branch, branch_id)

def get_branches(db: Session, skip: int = 0, limit: int = 100, **filters) -> List[Branch]:
    query = select(Branch)
    if filters:
        filter_clauses = [getattr(Branch, k) == v for k, v in filters.items() if hasattr(Branch, k)]
        query = query.where(and_(*filter_clauses))
    return list(db.execute(query.offset(skip).limit(limit)).scalars().all())

def update_branch(db: Session, branch_id: int, updates: Dict[str, Any]) -> Optional[Branch]:
    return update_entity(db, Branch, branch_id, updates)

def delete_branch(db: Session, branch_id: int) -> bool:
    return delete_entity(db, Branch, branch_id)


# --- TRANSACTIONS ---
def create_transaction(db: Session, transaction_data: Dict[str, Any], details: Optional[List[Dict[str, Any]]] = None) -> Transaction:
    try:
        # Create transaction
        db_transaction = Transaction(**transaction_data)
        db.add(db_transaction)
        db.flush() # Get transaction ID

        if details:
            for detail_data in details:
                # Add transaction ID to details
                detail_data["transaction_id"] = db_transaction.id
                db_detail = TransactionDetail(**detail_data)
                db.add(db_detail)
                
                # Update stock
                product = db.get(Product, db_detail.product_id)
                if product:
                    product.stock = max(0, product.stock - db_detail.quantity)
                    logger.info(f"Reduced stock for product {product.id} by {db_detail.quantity}")
        
        db.commit()
        db.refresh(db_transaction)
        return db_transaction
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to create transaction: {e}")
        raise

def get_transaction(db: Session, transaction_id: int) -> Optional[Transaction]:
    return get_entity_by_id(db, Transaction, transaction_id)

def get_transactions(db: Session, skip: int = 0, limit: int = 100, **filters) -> List[Transaction]:
    query = select(Transaction)
    if filters:
        filter_clauses = [getattr(Transaction, k) == v for k, v in filters.items() if hasattr(Transaction, k)]
        query = query.where(and_(*filter_clauses))
    return list(db.execute(query.offset(skip).limit(limit)).scalars().all())

def update_transaction(db: Session, transaction_id: int, updates: Dict[str, Any]) -> Optional[Transaction]:
    return update_entity(db, Transaction, transaction_id, updates)

def delete_transaction(db: Session, transaction_id: int) -> bool:
    return delete_entity(db, Transaction, transaction_id)

def get_transaction_details(db: Session, transaction_id: int) -> List[TransactionDetail]:
    query = select(TransactionDetail).where(TransactionDetail.transaction_id == transaction_id)
    return db.execute(query).scalars().all()

# Legacy compatibility helper (shoud be removed later)
def execute_read(query: str, params: Optional[tuple] = None, theModel: Optional[Type[BaseModel]] = None):
    """
    DEPRECATED: Use ORM methods instead.
    Simple wrapper to maintain compatibility while migrating routers.
    """
    logger.warning(f"DEPRECATED: execute_read used with query: {query}")
    # This is a temporary hack for auth.py until it's fully migrated
    # It only supports simple "SELECT * FROM TABLE WHERE email = %s"
    db = SessionLocal()
    try:
        import re
        table_match = re.search(r"FROM (\w+)", query, re.IGNORECASE)
        email_match = re.search(r"email = %s", query, re.IGNORECASE)
        
        if table_match and email_match and params:
            table_name = table_match.group(1).upper()
            email = params[0]
            
            if table_name == "CUSTOMERS":
                stmt = select(Customer).where(Customer.email == email)
                result = db.execute(stmt).scalar_one_or_none()
            elif table_name == "EMPLOYEES":
                stmt = select(Employee).where(Employee.email == email)
                result = db.execute(stmt).scalar_one_or_none()
            else:
                return None
                
            if result and theModel:
                return theModel.model_validate(result)
            return result
        return None
    finally:
        db.close()
