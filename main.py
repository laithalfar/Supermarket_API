from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Import routers
from src.api.routers import (
    customers_router,
    employees_router,
    products_router,
    branches_router,
    transactions_router,
    auth_router
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

# Include routers with /api/v1 prefix
app.include_router(customers_router, prefix="/api/v1")
app.include_router(employees_router, prefix="/api/v1")
app.include_router(products_router, prefix="/api/v1")
app.include_router(branches_router, prefix="/api/v1")
app.include_router(transactions_router, prefix="/api/v1")
app.include_router(auth_router, prefix="/api/v1")

# Serve static files
app.mount("/static", StaticFiles(directory="frontend"), name="static")

# Root endpoint - Serve Login/Role Selection
@app.get("/", tags=["UI"])
async def root():
    return FileResponse("frontend/login.html")

# Signup Page
@app.get("/signup", tags=["UI"])
async def signup_page():
    return FileResponse("frontend/signup.html")

# Admin Dashboard
@app.get("/admin", tags=["UI"])
async def admin_panel():
    return FileResponse("frontend/index.html")

# Customer Portal
@app.get("/shop", tags=["UI"])
async def shop_portal():
    return FileResponse("frontend/user.html")

# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "healthy"}

# Run the app
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
