from fastapi import APIRouter, HTTPException
from typing import List
from datetime import date

from src.model.MODEL import EmployeeCreate, EmployeeInDB, EmployeeUpdate, Role
from src.crud.CRUD import get_employee, create_employee, update_employee, delete_employee

# Create router
router = APIRouter(prefix="/employees", tags=["employees"])

# Create employee
@router.post("/", response_model=EmployeeInDB, status_code=201)
async def create_employee_route(employee: EmployeeCreate):
    try:
        return create_employee(employee.model_dump())
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Read employees
@router.get("/", response_model=List[EmployeeInDB])
async def read_employees(skip: int = 0, limit: int = 100, role: Role = None):
    try:
        filters = {}
        if role:
            filters["role"] = role
        return get_employees(skip=skip, limit=limit, **filters)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Read employee
@router.get("/{employee_id}", response_model=EmployeeInDB)
async def read_employee(employee_id: int):
    employee = get_employee(employee_id)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    return employee

# Update employee
@router.put("/{employee_id}", response_model=EmployeeInDB)
async def update_employee_route(employee_id: int, employee: EmployeeUpdate):
    try:
        updated = update_employee(employee_id, employee.model_dump(exclude_unset=True))
        if not updated:
            raise HTTPException(status_code=404, detail="Employee not found")
        return updated
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Delete employee
@router.delete("/{employee_id}", status_code=204)
async def delete_employee_route(employee_id: int):
    success = delete_employee(employee_id)
    if not success:
        raise HTTPException(status_code=404, detail="Employee not found")
    return None

# Get active employees
@router.get("/active/", response_model=List[EmployeeInDB])
async def get_active_employees():
    try:
        return get_employees(date_of_end_employment=None)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
