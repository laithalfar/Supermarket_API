# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import routers
from src.api.routers import (
    customers_router,
    employees_router,
    products_router,
    branches_router,
    transactions_router
)

# Initialize FastAPI app
app = FastAPI(
    title="Supermarket Management System API",
    description="REST API for managing supermarket operations",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# CORS middleware configuration
# CORS (Cross-Origin Resource Sharing) middleware is server-side code that helps web applications 
# securely share resources across different domains by adding specific HTTP headers
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(customers_router)
app.include_router(employees_router)
app.include_router(products_router)
app.include_router(branches_router)
app.include_router(transactions_router)

# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    return {
        "message": "Welcome to Supermarket Management System API",
        "docs": "/api/docs",
        "redoc": "/api/redoc"
    }

# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "healthy"}

# Run the app
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
