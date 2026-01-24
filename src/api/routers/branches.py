from fastapi import APIRouter, HTTPException, Depends
from typing import List
from sqlalchemy.orm import Session
from src.database import get_db
from src.model.MODEL import BranchCreate, BranchInDB, BranchUpdate, TokenData
from src.crud import CRUD
from src.utils.security import get_current_user

# Create router
router = APIRouter(
    prefix="/branches", 
    tags=["branches"],
    dependencies=[Depends(get_current_user)]
)

# List branches
@router.get("/", response_model=List[BranchInDB])
async def list_branches(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return CRUD.get_branches(db, skip=skip, limit=limit)

# Create branch
@router.post("/", response_model=BranchInDB, status_code=201)
async def create_branch_route(branch: BranchCreate, db: Session = Depends(get_db)):
    try:
        return CRUD.create_branch(db, branch.model_dump())
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Read branch
@router.get("/{branch_id}", response_model=BranchInDB)
async def read_branch(branch_id: int, db: Session = Depends(get_db)):
    branch = CRUD.get_branch(db, branch_id)
    if not branch:
        raise HTTPException(status_code=404, detail="Branch not found")
    return branch

# Update branch
@router.put("/{branch_id}", response_model=BranchInDB)
async def update_branch_route(branch_id: int, branch: BranchUpdate, db: Session = Depends(get_db)):
    try:
        updated = CRUD.update_branch(db, branch_id, branch.model_dump(exclude_unset=True))
        if not updated:
            raise HTTPException(status_code=404, detail="Branch not found")
        return updated
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Delete branch
@router.delete("/{branch_id}", status_code=204)
async def delete_branch_route(branch_id: int, db: Session = Depends(get_db)):
    success = CRUD.delete_branch(db, branch_id)
    if not success:
        raise HTTPException(status_code=404, detail="Branch not found")
    return None

# Get branches by location
@router.get("/location/{location}", response_model=List[BranchInDB])
async def get_branches_by_location(location: str, db: Session = Depends(get_db)):
    try:
        return CRUD.get_branches(db, location=location)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
