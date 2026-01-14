from fastapi import APIRouter, HTTPException, Depends
from typing import List
import os
import sys

from src.model.MODEL import BranchCreate, BranchInDB, BranchUpdate, TokenData
from src.crud.CRUD import get_branch, get_branches, create_branch, update_branch, delete_branch
from src.utils.security import get_current_user

# Create router
router = APIRouter(
    prefix="/branches", 
    tags=["branches"],
    dependencies=[Depends(get_current_user)]
)

# List branches
@router.get("/", response_model=List[BranchInDB])
async def list_branches(skip: int = 0, limit: int = 100):
    return get_branches(skip=skip, limit=limit)

# Create branch
@router.post("/", response_model=BranchInDB, status_code=201)
async def create_branch_route(branch: BranchCreate):

    # Validate branch data
    try:
        return create_branch(branch.model_dump())
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Read branch
@router.get("/{branch_id}", response_model=BranchInDB)
async def read_branch(branch_id: int):
    branch = get_branch(branch_id)
    if not branch:
        raise HTTPException(status_code=404, detail="Branch not found")
    return branch

# Update branch
@router.put("/{branch_id}", response_model=BranchInDB)
async def update_branch_route(branch_id: int, branch: BranchUpdate):
    try:
        updated = update_branch(branch_id, branch.model_dump(exclude_unset=True))
        if not updated:
            raise HTTPException(status_code=404, detail="Branch not found")
        return updated
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Delete branch
@router.delete("/{branch_id}", status_code=204)
async def delete_branch_route(branch_id: int):
    success = delete_branch(branch_id)
    if not success:
        raise HTTPException(status_code=404, detail="Branch not found")
    return None

# Get branches by location
@router.get("/location/{location}", response_model=List[BranchInDB])
async def get_branches_by_location(location: str):
    try:
        return get_branches(location=location)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
