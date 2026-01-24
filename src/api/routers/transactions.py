from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from datetime import date
from sqlalchemy.orm import Session
from src.database import get_db
from src.model.MODEL import (
    TransactionCreate, TransactionInDB, TransactionResponse,
    TransactionDetailInDB, TokenData
)
from src.crud import CRUD
from src.utils.security import get_current_user

# Create router
router = APIRouter(
    prefix="/transactions", 
    tags=["transactions"],
    dependencies=[Depends(get_current_user)]
)

# Create transaction route
@router.post("/", response_model=TransactionInDB, status_code=201)
async def create_transaction_route(transaction: TransactionCreate, db: Session = Depends(get_db)):
    try:
        transaction_data = transaction.model_dump(exclude={"details"})
        details_data = [detail.model_dump() for detail in transaction.details]
        
        db_transaction = CRUD.create_transaction(db, transaction_data, details_data)
        return db_transaction
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Read transactions
@router.get("/", response_model=List[TransactionInDB])
async def read_transactions(
    skip: int = 0,
    limit: int = 100,
    branch_id: Optional[int] = None,
    customer_id: Optional[int] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db)
):
    try:
        filters = {}
        if branch_id is not None:
            filters["branch_id"] = branch_id
        if customer_id is not None:
            filters["customer_id"] = customer_id
        if start_date:
            filters["dateOfTransaction__gte"] = start_date
        if end_date:
            filters["dateOfTransaction__lte"] = end_date
            
        return CRUD.get_transactions(db, skip=skip, limit=limit, **filters)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Read transaction
@router.get("/{transaction_id}", response_model=TransactionResponse)
async def read_transaction(transaction_id: int, db: Session = Depends(get_db)):
    transaction = CRUD.get_transaction(db, transaction_id)
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    details = CRUD.get_transaction_details(db, transaction_id)
    
    # Merge transaction and details for response
    # We can use Pydantic to do this properly
    response_data = transaction.__dict__.copy()
    response_data["details"] = details
    return response_data

# Read transaction details
@router.get("/{transaction_id}/details", response_model=List[TransactionDetailInDB])
async def read_transaction_details(transaction_id: int, db: Session = Depends(get_db)):
    details = CRUD.get_transaction_details(db, transaction_id)
    if not details:
        raise HTTPException(
            status_code=404,
            detail="No details found for this transaction"
        )
    return details

# Update transaction
@router.put("/{transaction_id}", response_model=TransactionInDB)
async def update_transaction_route(
    transaction_id: int,
    transaction: dict,
    db: Session = Depends(get_db)
):
    try:
        updated = CRUD.update_transaction(db, transaction_id, transaction)
        if not updated:
            raise HTTPException(status_code=404, detail="Transaction not found")
        return updated
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Delete transaction
@router.delete("/{transaction_id}", status_code=204)
async def delete_transaction_route(transaction_id: int, db: Session = Depends(get_db)):
    success = CRUD.delete_transaction(db, transaction_id)
    if not success:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return None

# Get customer transactions
@router.get("/customer/{customer_id}", response_model=List[TransactionInDB])
async def get_customer_transactions(customer_id: int, db: Session = Depends(get_db)):
    try:
        return CRUD.get_transactions(db, customer_id=customer_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Get branch transactions
@router.get("/branch/{branch_id}", response_model=List[TransactionInDB])
async def get_branch_transactions(branch_id: int, db: Session = Depends(get_db)):
    try:
        return CRUD.get_transactions(db, branch_id=branch_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
