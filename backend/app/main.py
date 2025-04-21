from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import products, chat, recommendations
from app.database import engine, Base
import os
import json
from dotenv import load_dotenv
import logging

# Configure logging - reduce verbosity
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv(verbose=False)

# Initialize database models
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="SmartShelf API",
    description="API for managing perishable products and predicting expiration dates",
    version="0.1.0",
)

# Configure CORS
# Get list of allowed origins from environment variable or use default
origins_env = os.getenv("BACKEND_CORS_ORIGINS", '["http://localhost:3000", "http://frontend:3000"]')
try:
    origins = json.loads(origins_env)
except json.JSONDecodeError:
    origins = ["http://localhost:3000", "http://frontend:3000"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(products.router, prefix="/api", tags=["products"])
app.include_router(chat.router, prefix="/api", tags=["chat"])
app.include_router(recommendations.router, prefix="/api", tags=["recommendations"])

@app.get("/")
async def root():
    return {"message": "Welcome to SmartShelf API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/api/test")
async def test_api():
    """Simple test endpoint to verify API is working"""
    return [
        {"message": "API is working", "status": "ok"},
        {"message": "Second item", "status": "ok"}
    ] 