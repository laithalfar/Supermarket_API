from fastapi import APIRouter, HTTPException
from typing import List

from src.model.MODEL import CustomerCreate, CustomerInDB, CustomerUpdate
from CRUD import get_customer, create_customer, update_customer, delete_customer

# Create router
router = APIRouter(prefix="/customers", tags=["customers"]) 

# Create customer
@router.post("/", response_model=CustomerInDB, status_code=201)
async def create_customer_route(customer: CustomerCreate):
    try:
        return create_customer(customer.model_dump())
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Read customer
@router.get("/{customer_id}", response_model=CustomerInDB)
async def read_customer(customer_id: int):
    customer = get_customer(customer_id)
    if customer is None:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer

# Update customer
@router.put("/{customer_id}", response_model=CustomerInDB)
async def update_customer_route(customer_id: int, customer: CustomerUpdate):
    try:
        updated = update_customer(customer_id, customer.model_dump(exclude_unset=True))
        if updated is None:
            raise HTTPException(status_code=404, detail="Customer not found")
        return updated
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Delete customer
@router.delete("/{customer_id}", status_code=204)
async def delete_customer_route(customer_id: int):
    success = delete_customer(customer_id)
    if not success:
        raise HTTPException(status_code=404, detail="Customer not found")
    return None
