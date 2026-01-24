from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from sqlalchemy.orm import Session
from src.database import get_db
from src.model.MODEL import ProductCreate, ProductInDB, ProductUpdate, TokenData
from src.crud import CRUD
from src.utils.security import get_current_user

# Create router 
router = APIRouter(
    prefix="/products", 
    tags=["products"],
    dependencies=[Depends(get_current_user)]
)

# create product route
@router.post("/", response_model=ProductInDB, status_code=201)
async def create_product_route(product: ProductCreate, db: Session = Depends(get_db)):
    try:
        return CRUD.create_product(db, product.model_dump())
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Read products
@router.get("/", response_model=List[ProductInDB])
async def read_products(
    skip: int = 0, 
    limit: int = 100,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    category: Optional[str] = None,
    db: Session = Depends(get_db)
):
    try:
        filters = {}
        if min_price is not None:
            filters["sellPrice__gte"] = min_price
        if max_price is not None:
            filters["sellPrice__lte"] = max_price
        if category:
            filters["category"] = category
            
        return CRUD.get_products(db, skip=skip, limit=limit, **filters)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Read product
@router.get("/{product_id}", response_model=ProductInDB)
async def read_product(product_id: int, db: Session = Depends(get_db)):
    product = CRUD.get_product(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

# Update product
@router.put("/{product_id}", response_model=ProductInDB)
async def update_product_route(product_id: int, product: ProductUpdate, db: Session = Depends(get_db)):
    try:
        updated = CRUD.update_product(db, product_id, product.model_dump(exclude_unset=True))
        if not updated:
            raise HTTPException(status_code=404, detail="Product not found")
        return updated
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Delete product
@router.delete("/{product_id}", status_code=204)
async def delete_product_route(product_id: int, db: Session = Depends(get_db)):
    success = CRUD.delete_product(db, product_id)
    if not success:
        raise HTTPException(status_code=404, detail="Product not found")
    return None

# Get products by category
@router.get("/category/{category}", response_model=List[ProductInDB])
async def get_products_by_category(category: str, db: Session = Depends(get_db)):
    try:
        return CRUD.get_products(db, category=category)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
