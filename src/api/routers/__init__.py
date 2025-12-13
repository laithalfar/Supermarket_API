from .customers import router as customers_router
from .employees import router as employees_router
from .products import router as products_router
from .branches import router as branches_router
from .transactions import router as transactions_router

__all__ = [
    'customers_router',
    'employees_router',
    'products_router',
    'branches_router',
    'transactions_router'
]
