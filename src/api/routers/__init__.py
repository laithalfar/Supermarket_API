'''
FAST API ROUTER

- This file is used to initialize the routers
- It imports all the routers from the other files
- It exports all the routers to the main file with a new name
- It initializes the API router interaction with HTTP methods using TCP/IP
- It is used to translate the requests and responses to and from the API
'''


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
