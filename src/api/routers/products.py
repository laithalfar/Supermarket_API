from fastapi import APIRouter, HTTPException
from typing import List, Optional
from decimal import Decimal

from src.model.MODEL import ProductCreate, ProductInDB, ProductUpdate
from src.crud.CRUD import get_product, create_product, update_product, delete_product, get_products

# Create router 
router = APIRouter(prefix="/products", tags=["products"])

# create product route
@router.post("/", response_model=ProductInDB, status_code=201)
async def create_product_route(product: ProductCreate):
    try:
        return create_product(product.model_dump())
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Read products
@router.get("/", response_model=List[ProductInDB])
async def read_products(
    skip: int = 0, 
    limit: int = 100,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    category: Optional[str] = None
):
    try:
        filters = {}
        if min_price is not None:
            filters["sell_price__gte"] = min_price
        if max_price is not None:
            filters["sell_price__lte"] = max_price
        if category:
            filters["category"] = category
            
        return get_products(skip=skip, limit=limit, **filters)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Read product
@router.get("/{product_id}", response_model=ProductInDB)
async def read_product(product_id: int):
    product = get_product(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

# Update product
@router.put("/{product_id}", response_model=ProductInDB)
async def update_product_route(product_id: int, product: ProductUpdate):
    try:
        updated = update_product(product_id, product.model_dump(exclude_unset=True))
        if not updated:
            raise HTTPException(status_code=404, detail="Product not found")
        return updated
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Delete product
@router.delete("/{product_id}", status_code=204)
async def delete_product_route(product_id: int):
    success = delete_product(product_id)
    if not success:
        raise HTTPException(status_code=404, detail="Product not found")
    return None

# Get products by category
@router.get("/category/{category}", response_model=List[ProductInDB])
async def get_products_by_category(category: str):
    try:
        return get_products(category=category)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
