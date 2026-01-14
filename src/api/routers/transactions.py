from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from datetime import date, datetime

from src.model.MODEL import (
    TransactionCreate, TransactionInDB, TransactionResponse,
    TransactionDetailInDB, TransactionDetails, TokenData
)
from src.crud.CRUD import (
    get_transaction, create_transaction,
    update_transaction, delete_transaction, get_transaction_details,
    get_transactions
)
from src.utils.security import get_current_user

# Create router
router = APIRouter(
    prefix="/transactions", 
    tags=["transactions"],
    dependencies=[Depends(get_current_user)]
)

# Create transaction route
@router.post("/", response_model=TransactionInDB, status_code=201)
async def create_transaction_route(transaction: TransactionCreate):
    try:
        # Convert the transaction details to the format expected by CRUD
        transaction_data = transaction.model_dump()
        details = transaction_data.pop("details", [])
        
        # Create the transaction with details
        created_transaction = create_transaction(transaction_data, details)
        return created_transaction
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
    end_date: Optional[date] = None
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
            
        return get_transactions(skip=skip, limit=limit, **filters)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Read transaction
@router.get("/{transaction_id}", response_model=TransactionResponse)
async def read_transaction(transaction_id: int):
    transaction = get_transaction(transaction_id)
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    # Get transaction details
    details = get_transaction_details(transaction_id)
    
    # Create response with details
    response = TransactionResponse(
        **transaction.model_dump(),
        details=[TransactionDetailInDB.model_validate(d) for d in details] if isinstance(details, list) else []
    )
    return response

# Read transaction details
@router.get("/{transaction_id}/details", response_model=List[TransactionDetailInDB])
async def read_transaction_details(transaction_id: int):
    details = get_transaction_details(transaction_id)
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
    transaction: dict  # Using dict to allow partial updates
):
    try:
        updated = update_transaction(transaction_id, transaction)
        if not updated:
            raise HTTPException(status_code=404, detail="Transaction not found")
        return updated
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Delete transaction
@router.delete("/{transaction_id}", status_code=204)
async def delete_transaction_route(transaction_id: int):
    success = delete_transaction(transaction_id)
    if not success:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return None

# Get customer transactions
@router.get("/customer/{customer_id}", response_model=List[TransactionInDB])
async def get_customer_transactions(customer_id: int):
    try:
        return get_transactions(customer_id=customer_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Get branch transactions
@router.get("/branch/{branch_id}", response_model=List[TransactionInDB])
async def get_branch_transactions(branch_id: int):
    try:
        return get_transactions(branch_id=branch_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
